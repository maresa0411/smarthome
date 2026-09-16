from unittest.mock import Mock

import pytest

from smarthome.model.door_sensor import DoorSensor


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def sensor(mqtt_client):
    return DoorSensor("test_door", mqtt_client)


def test_initial_state(sensor):
    assert sensor.is_closed is None
    assert sensor.is_battery_low is None
    assert sensor.is_tamper_proof is None
    assert sensor.battery is None
    assert sensor.voltage is None


def test_battery(sensor):
    sensor.state = {"battery": 73}

    assert sensor.battery == 73


def test_voltage(sensor):
    sensor.state = {"voltage": 2900}

    assert sensor.voltage == 2900


def test_battery_low_true(sensor):
    sensor.state = {"battery_low": True}

    assert sensor.is_battery_low is True


def test_battery_low_false(sensor):
    sensor.state = {"battery_low": False}

    assert sensor.is_battery_low is False


def test_tamper_true(sensor):
    sensor.state = {"tamper": True}

    assert sensor.is_tamper_proof is False


def test_tamper_false(sensor):
    sensor.state = {"tamper": False}

    assert sensor.is_tamper_proof is True


def test_tamper_missing(sensor):
    sensor.state = {}

    assert sensor.is_tamper_proof is None


def test_all_properties(sensor):
    sensor.state = {
        "contact": False,
        "battery_low": False,
        "tamper": False,
        "battery": 91,
        "voltage": 3000,
    }

    assert sensor.is_closed is True
    assert sensor.is_battery_low is False
    assert sensor.is_tamper_proof is True
    assert sensor.battery == 91
    assert sensor.voltage == 3000