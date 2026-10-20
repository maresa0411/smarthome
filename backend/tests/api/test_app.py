from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

from smarthome.api.app import app
from smarthome.api.dependencies import get_home
from smarthome.model.smart_home import SmartHome


@pytest.fixture
def home():
  return create_autospec(SmartHome, instance=True)


@pytest.fixture
def client(home):
  app.dependency_overrides[get_home] = lambda: home
  yield TestClient(app)
  app.dependency_overrides.clear()


def test_add_device_success(client, home):
  response = client.post(
      "/add_device", json={"name": "wohnzimmer_licht", "type": "light"}
  )

  assert response.status_code == 204
  home.create_and_add_device.assert_called_once_with("wohnzimmer_licht", "light")


def test_add_device_invalid_type(client, home):
  response = client.post(
      "/add_device", json={"name": "bad_device", "type": "invalid_toaster_type"}
  )

  assert response.status_code == 422
  error = response.json()["detail"][0]
  assert error["loc"] == ["body", "type"]
  assert "invalid_toaster_type" in error["msg"]
  home.create_and_add_device.assert_not_called()

def test_add_device_already_exists(client, home):
  home.create_and_add_device.side_effect = ValueError(
      "Device 'wohnzimmer_licht' already exists."
  )

  response = client.post(
      "/add_device", json={"name": "wohnzimmer_licht", "type": "light"}
  )

  assert response.status_code == 400

# -------------------------------------------------------------------
# remove_device
# -------------------------------------------------------------------

def test_remove_device_success(client, home):
    response = client.delete("/remove_device", params={"name": "kommode"})

    assert response.status_code == 204
    assert response.content == b""
    home.remove_device.assert_called_once_with("kommode")


def test_remove_unknown_device_returns_404(client, home):
    home.remove_device.side_effect = KeyError("unknown")

    response = client.delete("/remove_device", params={"name": "unknown"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Device 'unknown' not found"}


def test_remove_device_without_name_returns_422(client, home):
    response = client.delete("/remove_device")

    assert response.status_code == 422
    home.remove_device.assert_not_called()


def test_remove_device_name_in_body_is_not_accepted(client, home):
    response = client.request(
        "DELETE", "/remove_device", json={"name": "kommode"}
    )

    assert response.status_code == 422
    home.remove_device.assert_not_called()


def test_remove_device_with_post_is_not_allowed(client, home):
    response = client.post("/remove_device", params={"name": "kommode"})

    assert response.status_code == 405
    home.remove_device.assert_not_called()


def test_remove_device_name_with_special_characters(client, home):
    response = client.delete(
        "/remove_device", params={"name": "wohnzimmer licht/1"}
    )

    assert response.status_code == 204
    home.remove_device.assert_called_once_with("wohnzimmer licht/1")


def test_remove_device_other_errors_are_not_swallowed(home):
    from fastapi.testclient import TestClient

    from smarthome.api.app import app
    from smarthome.api.dependencies import get_home

    home.remove_device.side_effect = RuntimeError("boom")
    app.dependency_overrides[get_home] = lambda: home

    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.delete("/remove_device", params={"name": "x"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500