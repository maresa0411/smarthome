import json
from unittest.mock import Mock

import pytest

from smarthome.model.climate_sensor import ClimateSensor


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def sensor(mqtt_client):
    return ClimateSensor("test_sensor", mqtt_client)


def test_initial_state(sensor):
    assert sensor.battery is None
    assert sensor.temperature is None
    assert sensor.humidity is None
    assert sensor.temperature_calibration is None
    assert sensor.humidity_calibration is None


def test_properties(sensor):
    sensor.state = {
        "battery": 85,
        "temperature": 23.5,
        "humidity": 57.2,
        "temperature_calibration": -1.5,
        "humidity_calibration": 2.0,
    }

    assert sensor.battery == 85
    assert sensor.temperature == 23.5
    assert sensor.humidity == 57.2
    assert sensor.temperature_calibration == -1.5
    assert sensor.humidity_calibration == 2.0


def test_set_temperature_calibration(sensor, mqtt_client):
    sensor.set_temperature_calibration(5)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_sensor/set",
        json.dumps({"temperature_calibration": 5})
    )


@pytest.mark.parametrize("value", [-50, 0, 12.5, 50])
def test_set_temperature_calibration_valid_values(
    sensor,
    mqtt_client,
    value
):
    sensor.set_temperature_calibration(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_sensor/set",
        json.dumps({"temperature_calibration": value})
    )


@pytest.mark.parametrize("value", [-50.1, 50.1, -100, 100])
def test_set_temperature_calibration_out_of_range(sensor, value):
    with pytest.raises(ValueError):
        sensor.set_temperature_calibration(value)


@pytest.mark.parametrize("value", ["5", None, [], {}])
def test_set_temperature_calibration_invalid_type(sensor, value):
    with pytest.raises(TypeError):
        sensor.set_temperature_calibration(value)


def test_set_humidity_calibration(sensor, mqtt_client):
    sensor.set_humidity_calibration(-5)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_sensor/set",
        json.dumps({"humidity_calibration": -5})
    )


@pytest.mark.parametrize("value", [-50, 0, 12.5, 50])
def test_set_humidity_calibration_valid_values(
    sensor,
    mqtt_client,
    value
):
    sensor.set_humidity_calibration(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_sensor/set",
        json.dumps({"humidity_calibration": value})
    )


@pytest.mark.parametrize("value", [-50.1, 50.1, -100, 100])
def test_set_humidity_calibration_out_of_range(sensor, value):
    with pytest.raises(ValueError):
        sensor.set_humidity_calibration(value)


@pytest.mark.parametrize("value", ["5", None, [], {}])
def test_set_humidity_calibration_invalid_type(sensor, value):
    with pytest.raises(TypeError):
        sensor.set_humidity_calibration(value)