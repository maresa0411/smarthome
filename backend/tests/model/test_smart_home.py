import json
from unittest.mock import Mock, patch

import pytest

from smarthome.model.device import Device
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def home(mqtt_client):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        home = SmartHome("localhost", 1883)

    return home


@pytest.fixture
def device(mqtt_client):
    return Device("test_device", mqtt_client)


def test_initialization(mqtt_client):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        home = SmartHome("localhost", 1883)

    assert home.devices == {}
    assert home.devices_by_topic == {}

    mqtt_client.connect.assert_called_once_with(
        "localhost",
        1883
    )


def test_add_device(home, device):
    home.add_device(device)

    assert home.devices["test_device"] is device
    assert (
        home.devices_by_topic["zigbee2mqtt/test_device"]
        is device
    )


def test_add_devices(home, mqtt_client):
    device1 = Device("device1", mqtt_client)
    device2 = Device("device2", mqtt_client)

    home.add_devices(device1, device2)

    assert home.devices["device1"] is device1
    assert home.devices["device2"] is device2

    assert (
        home.devices_by_topic["zigbee2mqtt/device1"]
        is device1
    )
    assert (
        home.devices_by_topic["zigbee2mqtt/device2"]
        is device2
    )


def test_add_duplicate_name_raises_value_error(
    home,
    mqtt_client
):
    device1 = Device("test", mqtt_client)
    device2 = Device("test", mqtt_client)

    home.add_device(device1)

    with pytest.raises(
        ValueError,
        match="Device 'test' already exists."
    ):
        home.add_device(device2)


def test_add_duplicate_topic_raises_value_error(
    home,
    mqtt_client
):
    device1 = Device("device1", mqtt_client)
    device2 = Device("device2", mqtt_client)

    device2.topic = device1.topic

    home.add_device(device1)

    with pytest.raises(
        ValueError,
        match="Topic 'zigbee2mqtt/device1' is already registered."
    ):
        home.add_device(device2)


def test_remove_device(home, device):
    home.add_device(device)

    home.remove_device("test_device")

    assert "test_device" not in home.devices
    assert "zigbee2mqtt/test_device" not in home.devices_by_topic


def test_get_device(home, device):
    home.add_device(device)

    result = home.get_device("test_device")

    assert result is device


def test_get_unknown_device_returns_none(home):
    assert home.get_device("unknown") is None


def test_get_device_by_topic(home, device):
    home.add_device(device)

    result = home.get_device_by_topic(
        "zigbee2mqtt/test_device"
    )

    assert result is device


def test_get_unknown_topic_returns_none(home):
    assert home.get_device_by_topic(
        "zigbee2mqtt/unknown"
    ) is None


def test_on_message_updates_device(home, device):
    home.add_device(device)

    message = Mock()
    message.topic = "zigbee2mqtt/test_device"
    message.payload = json.dumps({
        "temperature": 23.5
    }).encode()

    home._on_message(
        home.mqtt_client,
        None,
        message
    )

    assert device.state == {
        "temperature": 23.5
    }


def test_on_message_unknown_topic_does_nothing(
    home,
    device
):
    home.add_device(device)

    message = Mock()
    message.topic = "zigbee2mqtt/unknown"
    message.payload = json.dumps({
        "temperature": 23.5
    }).encode()

    home._on_message(
        home.mqtt_client,
        None,
        message
    )

    assert device.state == {}


def test_on_message_invalid_json_does_nothing(
    home,
    device
):
    home.add_device(device)

    message = Mock()
    message.topic = "zigbee2mqtt/test_device"
    message.payload = b"invalid json"

    home._on_message(
        home.mqtt_client,
        None,
        message
    )

    assert device.state == {}


def test_on_connect_subscribes_devices(
    home,
    mqtt_client
):
    device1 = Mock(spec=Device)
    device1.name = "device1"
    device1.topic = "zigbee2mqtt/device1"

    device2 = Mock(spec=Device)
    device2.name = "device2"
    device2.topic = "zigbee2mqtt/device2"

    home.add_devices(device1, device2)

    home._on_connect(
        mqtt_client,
        None,
        None,
        None,
        None
    )

    assert mqtt_client.subscribe.call_count == 2

    mqtt_client.subscribe.assert_any_call(
        "zigbee2mqtt/device1"
    )
    mqtt_client.subscribe.assert_any_call(
        "zigbee2mqtt/device2"
    )


def test_on_connect_requests_state_from_devices(
    home,
    mqtt_client
):
    device1 = Mock(spec=Device)
    device1.name = "device1"
    device1.topic = "zigbee2mqtt/device1"

    device2 = Mock(spec=Device)
    device2.name = "device2"
    device2.topic = "zigbee2mqtt/device2"

    home.add_devices(device1, device2)

    home._on_connect(
        mqtt_client,
        None,
        None,
        None,
        None
    )

    device1.request_state.assert_called_once()
    device2.request_state.assert_called_once()


def test_start(home, mqtt_client):
    home.start()

    mqtt_client.loop_start.assert_called_once()


def test_stop(home, mqtt_client):
    home.stop()

    mqtt_client.loop_stop.assert_called_once()
    mqtt_client.disconnect.assert_called_once()