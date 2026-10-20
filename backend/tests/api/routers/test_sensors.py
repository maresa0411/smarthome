from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from smarthome.api.app import app
from smarthome.api.dependencies import get_home
from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def climate_sensor(mqtt_client):
    sensor = ClimateSensor(
        "test_climate",
        mqtt_client
    )

    sensor.state = {
        "battery": 100,
        "temperature": 23.5,
        "humidity": 55.0,
        "temperature_calibration": 0,
        "humidity_calibration": 0
    }

    return sensor


@pytest.fixture
def door_sensor(mqtt_client):
    sensor = DoorSensor(
        "test_door",
        mqtt_client
    )

    sensor.state = {
        "contact": False,
        "battery_low": False,
        "tamper": False,
        "battery": 90,
        "voltage": 3000
    }

    return sensor


@pytest.fixture
def home(mqtt_client, tmp_path, climate_sensor, door_sensor):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        home = SmartHome(
            "localhost", 1883,
            config_file=tmp_path / "devices.json"
        )

    home.add_devices(climate_sensor, door_sensor)
    return home

@pytest.fixture
def client(home):
    app.dependency_overrides[get_home] = lambda: home

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_get_climate_sensors(client):
    response = client.get(
        "/sensors/climateSensors"
    )

    assert response.status_code == 200

    assert response.json() == [
        {
            "name": "test_climate",
            "battery": 100,
            "temperature": 23.5,
            "humidity": 55.0,
            "temperature_calibration": 0,
            "humidity_calibration": 0
        }
    ]


def test_get_climate_sensor(client):
    response = client.get(
        "/sensors/climateSensors/test_climate"
    )

    assert response.status_code == 200

    assert response.json() == {
        "name": "test_climate",
        "battery": 100,
        "temperature": 23.5,
        "humidity": 55.0,
        "temperature_calibration": 0,
        "humidity_calibration": 0
    }


def test_get_unknown_climate_sensor(client):
    response = client.get(
        "/sensors/climateSensors/unknown"
    )

    assert response.status_code == 404


def test_climate_sensor_without_data(
    client,
    climate_sensor
):
    climate_sensor.state = {}

    response = client.get(
        "/sensors/climateSensors/test_climate"
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Sensor data is not available yet"
    }


def test_get_door_sensors(client):
    response = client.get(
        "/sensors/doorSensors"
    )

    assert response.status_code == 200

    assert len(response.json()) == 1

    sensor = response.json()[0]

    assert sensor["name"] == "test_door"
    assert sensor["battery"] == 90
    assert sensor["voltage"] == 3000
    assert sensor["battery_low"] is False


def test_get_door_sensor(client):
    response = client.get(
        "/sensors/doorSensors/test_door"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test_door"


def test_get_unknown_door_sensor(client):
    response = client.get(
        "/sensors/doorSensors/unknown"
    )

    assert response.status_code == 404


def test_door_sensor_without_data(
    client,
    door_sensor
):
    door_sensor.state = {}

    response = client.get(
        "/sensors/doorSensors/test_door"
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Sensor data is not available yet"
    }


@pytest.mark.parametrize(
    "value",
    [-50, 0, 10.5, 50]
)
def test_set_valid_temperature_calibration(
    client,
    value
):
    response = client.post(
        "/sensors/climateSensors/"
        "test_climate/temperatureCalibration",
        json={
            "value": value
        }
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "value",
    [-50.1, 50.1]
)
def test_set_invalid_temperature_calibration(
    client,
    value
):
    response = client.post(
        "/sensors/climateSensors/"
        "test_climate/temperatureCalibration",
        json={
            "value": value
        }
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "value",
    [-50, 0, 10.5, 50]
)
def test_set_valid_humidity_calibration(
    client,
    value
):
    response = client.post(
        "/sensors/climateSensors/"
        "test_climate/humidityCalibration",
        json={
            "value": value
        }
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "value",
    [-50.1, 50.1]
)
def test_set_invalid_humidity_calibration(
    client,
    value
):
    response = client.post(
        "/sensors/climateSensors/"
        "test_climate/humidityCalibration",
        json={
            "value": value
        }
    )

    assert response.status_code == 422