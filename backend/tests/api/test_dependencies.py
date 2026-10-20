from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient

from smarthome.api.dependencies import get_home

from smarthome.api.dependencies import (
    _get_light_by_id,
    _get_door_sensor_by_id,
    _get_climate_sensor_by_id,
)
from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def home():
    return Mock(spec=SmartHome)

def test_get_home_returns_home_from_app_state(home):
    request = Mock()
    request.app.state.home = home

    assert get_home(request) is home


def test_get_home_with_real_app_state(home):
    app = FastAPI()
    app.state.home = home

    @app.get("/probe")
    def probe(h: SmartHome = Depends(get_home)):
        return {"same": h is home}

    client = TestClient(app)

    response = client.get("/probe")

    assert response.status_code == 200
    assert response.json() == {"same": True}


def test_get_home_without_state_raises_attribute_error():
    app = FastAPI()

    @app.get("/probe")
    def probe(h: SmartHome = Depends(get_home)):
        return {}

    client = TestClient(app, raise_server_exceptions=True)

    with pytest.raises(AttributeError):
        client.get("/probe")

def test_get_light_by_id_returns_light(home, mqtt_client):
    light = Light("test_light", mqtt_client)
    home.get_device.return_value = light

    result = _get_light_by_id("test_light", home)

    assert result is light
    home.get_device.assert_called_once_with("test_light")


def test_get_light_by_id_unknown_device(home):
    home.get_device.return_value = None

    with pytest.raises(HTTPException) as exc:
        _get_light_by_id("unknown", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Light not found"


def test_get_light_by_id_wrong_device_type(home, mqtt_client):
    sensor = ClimateSensor("test_sensor", mqtt_client)
    home.get_device.return_value = sensor

    with pytest.raises(HTTPException) as exc:
        _get_light_by_id("test_sensor", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Light not found"


def test_get_door_sensor_by_id_returns_door_sensor(
    home,
    mqtt_client
):
    sensor = DoorSensor("test_door", mqtt_client)
    home.get_device.return_value = sensor

    result = _get_door_sensor_by_id(
        "test_door",
        home
    )

    assert result is sensor
    home.get_device.assert_called_once_with(
        "test_door"
    )


def test_get_door_sensor_by_id_unknown_device(home):
    home.get_device.return_value = None

    with pytest.raises(HTTPException) as exc:
        _get_door_sensor_by_id("unknown", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Door Sensor not found"


def test_get_door_sensor_by_id_wrong_device_type(
    home,
    mqtt_client
):
    light = Light("test_light", mqtt_client)
    home.get_device.return_value = light

    with pytest.raises(HTTPException) as exc:
        _get_door_sensor_by_id("test_light", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Door Sensor not found"


def test_get_climate_sensor_by_id_returns_climate_sensor(
    home,
    mqtt_client
):
    sensor = ClimateSensor(
        "test_climate",
        mqtt_client
    )
    home.get_device.return_value = sensor

    result = _get_climate_sensor_by_id(
        "test_climate",
        home
    )

    assert result is sensor
    home.get_device.assert_called_once_with(
        "test_climate"
    )


def test_get_climate_sensor_by_id_unknown_device(home):
    home.get_device.return_value = None

    with pytest.raises(HTTPException) as exc:
        _get_climate_sensor_by_id("unknown", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Climate Sensor not found"


def test_get_climate_sensor_by_id_wrong_device_type(
    home,
    mqtt_client
):
    light = Light("test_light", mqtt_client)
    home.get_device.return_value = light

    with pytest.raises(HTTPException) as exc:
        _get_climate_sensor_by_id("test_light", home)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Climate Sensor not found"