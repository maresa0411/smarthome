import json
from unittest.mock import Mock

import pytest

from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.device import Device
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.light import Light


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def device(mqtt_client):
    return Device("test_device", mqtt_client)


def test_initialization(device):
    assert device.name == "test_device"
    assert device.topic == "zigbee2mqtt/test_device"
    assert device.state == {}


def test_set(device, mqtt_client):
    device.set({
        "state": "ON"
    })

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_device/set",
        json.dumps({
            "state": "ON"
        })
    )


def test_get(device, mqtt_client):
    device.get({
        "state": ""
    })

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_device/get",
        json.dumps({
            "state": ""
        })
    )


def test_on_message_updates_state(device):
    device.on_message({
        "temperature": 23.5
    })

    assert device.state == {
        "temperature": 23.5
    }


def test_on_message_preserves_existing_state(device):
    device.state = {
        "battery": 100
    }

    device.on_message({
        "temperature": 23.5
    })

    assert device.state == {
        "battery": 100,
        "temperature": 23.5
    }


def test_on_message_overwrites_existing_value(device):
    device.state = {
        "temperature": 20.0
    }

    device.on_message({
        "temperature": 23.5
    })

    assert device.state["temperature"] == 23.5


def test_request_state_does_nothing(device, mqtt_client):
    device.request_state()

    mqtt_client.publish.assert_not_called()


def test_repr(device):
    assert repr(device) == (
        "Device(name='test_device', "
        "topic='zigbee2mqtt/test_device')"
    )

# -------------------------------------------------------------------
# Registry
# -------------------------------------------------------------------

@pytest.fixture
def isolated_registry(monkeypatch):
    monkeypatch.setattr(Device, "registry", dict(Device.registry))
    return Device.registry


def test_subclass_is_registered(isolated_registry):
    class Thermostat(Device):
        pass

    assert isolated_registry["thermostat"] is Thermostat


def test_registry_key_is_lowercase_class_name(isolated_registry):
    class MyFancyDevice(Device):
        pass

    assert "myfancydevice" in isolated_registry
    assert "MyFancyDevice" not in isolated_registry


def test_device_itself_is_not_registered():
    assert "device" not in Device.registry


def test_indirect_subclass_is_registered(isolated_registry):
    class Base(Device):
        pass

    class Derived(Base):
        pass

    assert isolated_registry["base"] is Base
    assert isolated_registry["derived"] is Derived


def test_registry_is_shared_between_classes(isolated_registry):
    class Plug(Device):
        pass

    assert Plug.registry is Device.registry


def test_registering_does_not_affect_other_entries(isolated_registry):
    before = dict(isolated_registry)

    class Plug(Device):
        pass

    assert isolated_registry == {**before, "plug": Plug}


def test_same_class_name_overwrites_existing_entry(isolated_registry):
    class Plug(Device):
        pass

    first = Plug

    class Plug(Device):
        pass

    assert isolated_registry["plug"] is Plug
    assert isolated_registry["plug"] is not first


def test_registered_class_can_be_instantiated(isolated_registry, mqtt_client):
    class Plug(Device):
        pass

    device = isolated_registry["plug"]("wohnzimmer", mqtt_client)

    assert isinstance(device, Plug)
    assert device.topic == "zigbee2mqtt/wohnzimmer"


def test_builtin_devices_are_registered():
    assert Device.registry["light"] is Light
    assert Device.registry["climatesensor"] is ClimateSensor
    assert Device.registry["doorsensor"] is DoorSensor