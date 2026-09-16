import json
from unittest.mock import Mock

import pytest

from smarthome.model.device import Device


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