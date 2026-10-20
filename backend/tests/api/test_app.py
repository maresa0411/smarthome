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