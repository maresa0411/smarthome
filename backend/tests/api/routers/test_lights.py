from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from datetime import time

from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
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
def home(mqtt_client, tmp_path, light):
    with patch(
        "smarthome.model.smart_home.mqtt.Client",
        return_value=mqtt_client
    ):
        home = SmartHome(
            "localhost", 1883,
            config_file=tmp_path / "devices.json"
        )

    home.add_devices(light)
    return home

@pytest.fixture
def client(home):
    app.dependency_overrides[get_home] = lambda: home

    yield TestClient(app)

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

# -------------------------------------------------------------------
# get_lights
# -------------------------------------------------------------------

def test_get_lights_ignores_other_device_types(client, home, mqtt_client):
    home.add_devices(
        DoorSensor("test_door", mqtt_client),
        ClimateSensor("test_climate", mqtt_client),
    )

    response = client.get("/lights")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["test_light"]


def test_get_lights_returns_all_lights(client, home, mqtt_client):
    second = Light("second_light", mqtt_client)
    second.state = {"state": "OFF"}
    home.add_devices(second)

    response = client.get("/lights")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "test_light",
        "second_light",
    ]
    assert response.json()[1]["is_on"] is False


def test_get_lights_without_lights_returns_empty_list(client, home):
    home.remove_device("test_light")

    response = client.get("/lights")

    assert response.status_code == 200
    assert response.json() == []


def test_get_lights_only_other_devices_returns_empty_list(
    client, home, mqtt_client
):
    home.remove_device("test_light")
    home.add_devices(DoorSensor("test_door", mqtt_client))

    response = client.get("/lights")

    assert response.status_code == 200
    assert response.json() == []


# -------------------------------------------------------------------
# set_light_alarm
# -------------------------------------------------------------------

def test_set_light_alarm_with_required_fields_only(client, light):
    with patch.object(light, "set_light_alarm") as alarm:
        response = client.post(
            "/lights/test_light/set_light_alarm",
            json={"start_time": "07:00:00", "duration": 30},
        )

    assert response.status_code == 204

    alarm.assert_called_once_with(start_time=time(7, 0), duration=30)


def test_set_light_alarm_with_all_fields(client, light):
    with patch.object(light, "set_light_alarm") as alarm:
        response = client.post(
            "/lights/test_light/set_light_alarm",
            json={
                "start_time": "06:45:00",
                "duration": 15,
                "start_brightness": 10,
                "end_brightness": 200,
                "color": "#FF0000",
            },
        )

    assert response.status_code == 204

    alarm.assert_called_once_with(
        start_time=time(6, 45),
        duration=15,
        start_brightness=10,
        end_brightness=200,
        color="#FF0000",
    )


@pytest.mark.parametrize(
    "optional",
    [
        {"start_brightness": 10},
        {"end_brightness": 200},
        {"color": "#00FF00"},
    ],
)
def test_set_light_alarm_passes_only_given_optional_fields(
    client, light, optional
):
    with patch.object(light, "set_light_alarm") as alarm:
        response = client.post(
            "/lights/test_light/set_light_alarm",
            json={"start_time": "07:00:00", "duration": 30, **optional},
        )

    assert response.status_code == 204

    alarm.assert_called_once_with(
        start_time=time(7, 0), duration=30, **optional
    )


def test_set_light_alarm_starts_thread(client, light):
    # ohne Mock an der Methode: prüft die ganze Kette bis zum Thread
    with patch("smarthome.model.light.threading.Thread") as thread_class:
        response = client.post(
            "/lights/test_light/set_light_alarm",
            json={"start_time": "07:00:00", "duration": 30},
        )

    assert response.status_code == 204
    thread_class.assert_called_once()
    thread_class.return_value.start.assert_called_once()


def test_set_light_alarm_value_error_returns_400(client, light):
    with patch.object(
        light,
        "set_light_alarm",
        side_effect=ValueError("end_brightness must be greater than or equal to start_brightness."),
    ):
        response = client.post(
            "/lights/test_light/set_light_alarm",
            json={"start_time": "07:00:00", "duration": 30},
        )

    assert response.status_code == 400
    assert "end_brightness" in response.json()["detail"]


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"duration": 30},
        {"start_time": "07:00:00"},
        {"start_time": "kein datum", "duration": 30},
    ],
)
def test_set_light_alarm_invalid_body_returns_422(client, light, body):
    with patch.object(light, "set_light_alarm") as alarm:
        response = client.post(
            "/lights/test_light/set_light_alarm", json=body
        )

    assert response.status_code == 422
    alarm.assert_not_called()


def test_set_light_alarm_unknown_light(client):
    response = client.post(
        "/lights/unknown/set_light_alarm",
        json={"start_time": "07:00:00", "duration": 30},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Light not found"}


# -------------------------------------------------------------------
# cancel_light_alarm
# -------------------------------------------------------------------

def test_cancel_light_alarm(client, light):
    with patch.object(light, "cancel_light_alarm") as cancel:
        response = client.post("/lights/test_light/cancel_light_alarn")

    assert response.status_code == 204
    cancel.assert_called_once_with()


def test_cancel_light_alarm_stops_running_alarm(client, light):
    with patch("smarthome.model.light.threading.Thread"):
        client.post(
            "/lights/test_light/set_light_alarm",
            json={"start_time": "07:00:00", "duration": 30},
        )

    assert light._alarm_thread is not None

    client.post("/lights/test_light/cancel_light_alarn")

    assert light._alarm_stop_event.is_set()
    assert light._alarm_thread is None


def test_cancel_light_alarm_unknown_light(client):
    response = client.post("/lights/unknown/cancel_light_alarn")

    assert response.status_code == 404
    assert response.json() == {"detail": "Light not found"}