import json
from unittest.mock import Mock, patch
import paho.mqtt.client as mqtt
from pathlib import Path

from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.light import Light

import pytest

from smarthome.model.device import Device
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def home(mqtt_client, tmp_path):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        return SmartHome(
            "localhost", 1883,
            config_file=tmp_path / "devices.json"
        )


def build_home(mqtt_client, config_file):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        return SmartHome("localhost", 1883, config_file=config_file)


@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "devices.json"

@pytest.fixture
def device(mqtt_client):
    return Device("test_device", mqtt_client)


def test_initialization(mqtt_client, tmp_path):
    with patch("smarthome.model.smart_home.mqtt.Client", return_value=mqtt_client):
        home = SmartHome("localhost", 1883, config_file=tmp_path / "devices.json")

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

def test_initialization_registers_callbacks(mqtt_client, tmp_path):
    home = build_home(mqtt_client, tmp_path / "devices.json")

    assert mqtt_client.on_message == home._on_message
    assert mqtt_client.on_connect == home._on_connect


def test_initialization_uses_callback_api_version_2(mqtt_client, tmp_path):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ) as client_class:
        SmartHome("localhost", 1883, config_file=tmp_path / "devices.json")

    client_class.assert_called_once_with(mqtt.CallbackAPIVersion.VERSION2)


def test_default_config_file_is_relative_devices_json(
    mqtt_client, tmp_path, monkeypatch
):
    # chdir, damit die echte devices.json nie berührt wird
    monkeypatch.chdir(tmp_path)

    with patch("smarthome.model.smart_home.mqtt.Client", return_value=mqtt_client):
        home = SmartHome("localhost", 1883)

    assert home.config_file == Path("devices.json")


# -------------------------------------------------------------------
# create_and_add_device
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "device_type, expected_class",
    [
        ("light", Light),
        ("climatesensor", ClimateSensor),
        ("doorsensor", DoorSensor),
    ]
)
def test_create_and_add_device_creates_correct_class(
    home, mqtt_client, device_type, expected_class
):
    home.create_and_add_device("test", device_type)

    device = home.devices["test"]

    assert type(device) is expected_class
    assert device.mqtt_client is mqtt_client
    assert home.devices_by_topic["zigbee2mqtt/test"] is device


@pytest.mark.parametrize("device_type", ["LIGHT", "Light", "lIgHt"])
def test_create_and_add_device_type_is_case_insensitive(home, device_type):
    home.create_and_add_device("test", device_type)

    assert isinstance(home.devices["test"], Light)


def test_create_and_add_device_saves_by_default(home, config_file):
    home.create_and_add_device("wohnzimmer_licht", "light")

    assert json.loads(config_file.read_text(encoding="utf-8")) == [
        {"name": "wohnzimmer_licht", "type": "light"}
    ]


def test_create_and_add_device_without_save_does_not_write(home, config_file):
    home.create_and_add_device("test", "light", save=False)

    assert "test" in home.devices
    assert not config_file.exists()


def test_create_and_add_device_unknown_type_raises_value_error(
    home, config_file
):
    with pytest.raises(ValueError, match="Unknown device type: toaster"):
        home.create_and_add_device("test", "toaster")

    assert home.devices == {}
    assert not config_file.exists()


def test_create_and_add_device_duplicate_name_raises_value_error(
    home, config_file
):
    home.create_and_add_device("test", "light")
    content_before = config_file.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="Device 'test' already exists."):
        home.create_and_add_device("test", "doorsensor")

    # das erste Gerät bleibt unverändert, die Config auch
    assert isinstance(home.devices["test"], Light)
    assert config_file.read_text(encoding="utf-8") == content_before


# -------------------------------------------------------------------
# save_devices
# -------------------------------------------------------------------

def test_save_devices_writes_name_and_type(home, config_file, mqtt_client):
    home.add_devices(
        Light("licht", mqtt_client),
        DoorSensor("tuer", mqtt_client),
        ClimateSensor("klima", mqtt_client),
    )

    home.save_devices()

    assert json.loads(config_file.read_text(encoding="utf-8")) == [
        {"name": "licht", "type": "light"},
        {"name": "tuer", "type": "doorsensor"},
        {"name": "klima", "type": "climatesensor"},
    ]


def test_save_devices_without_devices_writes_empty_list(home, config_file):
    home.save_devices()

    assert json.loads(config_file.read_text(encoding="utf-8")) == []


def test_save_devices_overwrites_existing_file(home, config_file):
    config_file.write_text('[{"name": "alt", "type": "light"}]', encoding="utf-8")

    home.save_devices()

    assert json.loads(config_file.read_text(encoding="utf-8")) == []


# -------------------------------------------------------------------
# load_devices
# -------------------------------------------------------------------

def test_load_devices_without_config_file_does_nothing(mqtt_client, config_file):
    home = build_home(mqtt_client, config_file)

    assert home.devices == {}
    assert not config_file.exists()


def test_load_devices_creates_devices_from_config(mqtt_client, config_file):
    config_file.write_text(
        json.dumps([
            {"name": "licht", "type": "light"},
            {"name": "tuer", "type": "doorsensor"},
        ]),
        encoding="utf-8",
    )

    home = build_home(mqtt_client, config_file)

    assert set(home.devices) == {"licht", "tuer"}
    assert isinstance(home.devices["licht"], Light)
    assert isinstance(home.devices["tuer"], DoorSensor)
    assert home.devices_by_topic["zigbee2mqtt/licht"] is home.devices["licht"]


def test_load_devices_does_not_rewrite_config(mqtt_client, config_file):
    content = '[{"name": "licht", "type": "light"}]'
    config_file.write_text(content, encoding="utf-8")

    build_home(mqtt_client, config_file)

    # Datei bleibt byte-identisch (kein indent=2 durch save_devices)
    assert config_file.read_text(encoding="utf-8") == content


def test_load_devices_empty_list(mqtt_client, config_file):
    config_file.write_text("[]", encoding="utf-8")

    home = build_home(mqtt_client, config_file)

    assert home.devices == {}


def test_load_devices_unknown_type_raises_value_error(mqtt_client, config_file):
    config_file.write_text(
        '[{"name": "x", "type": "toaster"}]', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unknown device type: toaster"):
        build_home(mqtt_client, config_file)


def test_load_devices_invalid_json_raises(mqtt_client, config_file):
    config_file.write_text("kein json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        build_home(mqtt_client, config_file)


def test_save_and_load_roundtrip(mqtt_client, config_file):
    first = build_home(mqtt_client, config_file)
    first.create_and_add_device("licht", "light")
    first.create_and_add_device("klima", "climatesensor")

    second = build_home(mqtt_client, config_file)

    assert set(second.devices) == {"licht", "klima"}
    assert isinstance(second.devices["licht"], Light)
    assert isinstance(second.devices["klima"], ClimateSensor)


# -------------------------------------------------------------------
# remove_device
# -------------------------------------------------------------------

def test_remove_unknown_device_raises_key_error(home):
    with pytest.raises(KeyError):
        home.remove_device("unknown")


def test_removed_device_can_be_added_again(home, device):
    home.add_device(device)
    home.remove_device("test_device")

    home.add_device(device)

    assert home.devices["test_device"] is device


# -------------------------------------------------------------------
# _on_connect (Ergänzung)
# -------------------------------------------------------------------

def test_on_connect_without_devices_does_nothing(home, mqtt_client):
    home._on_connect(mqtt_client, None, None, None, None)

    mqtt_client.subscribe.assert_not_called()