from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from smarthome.api.app import app
from smarthome.api.dependencies import get_home
from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def light(mqtt_client):
    light = Light("test_light", mqtt_client)
    light.state = {
        "state": "ON",
        "brightness": 150,
        "color_temp": 300,
        "color": {
            "x": 0.5,
            "y": 0.4
        }
    }
    return light


@pytest.fixture
def home(light):
    home = Mock(spec=SmartHome)

    home.devices = {
        light.name: light
    }

    home.get_device.side_effect = home.devices.get

    return home


@pytest.fixture
def client(home):
    app.dependency_overrides[get_home] = lambda: home

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_get_lights(client):
    response = client.get("/lights")

    assert response.status_code == 200

    assert response.json() == [
        {
            "name": "test_light",
            "is_on": True,
            "brightness": 150,
            "color_temp": 300,
            "color": {
                "x": 0.5,
                "y": 0.4
            }
        }
    ]


def test_get_light(client):
    response = client.get("/lights/test_light")

    assert response.status_code == 200

    assert response.json() == {
        "name": "test_light",
        "is_on": True,
        "brightness": 150,
        "color_temp": 300,
        "color": {
            "x": 0.5,
            "y": 0.4
        }
    }


def test_get_unknown_light(client):
    response = client.get("/lights/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Light not found"
    }


def test_turn_on(client, light, mqtt_client):
    response = client.post(
        "/lights/test_light/turn_on"
    )

    assert response.status_code == 204

    mqtt_client.publish.assert_called_once()


def test_turn_off(client, light, mqtt_client):
    response = client.post(
        "/lights/test_light/turn_off"
    )

    assert response.status_code == 204

    mqtt_client.publish.assert_called_once()


def test_toggle(client, light, mqtt_client):
    response = client.post(
        "/lights/test_light/toggle"
    )

    assert response.status_code == 204

    mqtt_client.publish.assert_called_once()


@pytest.mark.parametrize(
    "value",
    [0, 1, 100, 254]
)
def test_set_valid_brightness(
    client,
    mqtt_client,
    value
):
    response = client.post(
        "/lights/test_light/brightness",
        json={
            "value": value
        }
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "value",
    [-1, 255]
)
def test_set_invalid_brightness(client, value):
    response = client.post(
        "/lights/test_light/brightness",
        json={
            "value": value
        }
    )

    assert response.status_code == 422


def test_set_color_temp(client):
    response = client.post(
        "/lights/test_light/color_temp",
        json={
            "color_temp": 300
        }
    )

    assert response.status_code == 204


def test_set_color(client):
    response = client.post(
        "/lights/test_light/color",
        json={
            "color": "#FF0000"
        }
    )

    assert response.status_code == 204


def test_turn_on_with_timed_off(client):
    response = client.post(
        "/lights/test_light/turn_on_with_timed_off",
        json={
            "seconds": 10
        }
    )

    assert response.status_code == 204


def test_turn_on_with_invalid_timer(client):
    response = client.post(
        "/lights/test_light/turn_on_with_timed_off",
        json={
            "seconds": 0
        }
    )

    assert response.status_code == 422