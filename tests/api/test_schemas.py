import pytest
from pydantic import ValidationError

from smarthome.api.schemas import (
    BrightnessRequest,
    ColorTempRequest,
    TimerRequest,
    ColorRequest,
    TemperatureCalibrationRequest,
    HumidityCalibrationRequest,
)


@pytest.mark.parametrize(
    "value",
    [0, 1, 100, 253, 254]
)
def test_brightness_valid(value):
    request = BrightnessRequest(value=value)

    assert request.value == value


@pytest.mark.parametrize(
    "value",
    [-1, 255, 1000]
)
def test_brightness_out_of_range(value):
    with pytest.raises(ValidationError):
        BrightnessRequest(value=value)


@pytest.mark.parametrize(
    "value",
    [153, 200, 300, 499, 500]
)
def test_color_temp_numeric_valid(value):
    request = ColorTempRequest(
        color_temp=value
    )

    assert request.color_temp == value


@pytest.mark.parametrize(
    "value",
    [152, 501]
)
def test_color_temp_numeric_out_of_range(value):
    with pytest.raises(ValidationError):
        ColorTempRequest(color_temp=value)


def test_color_temp_string_valid():
    request = ColorTempRequest(
        color_temp="coolest"
    )

    assert request.color_temp == "coolest"


@pytest.mark.parametrize(
    "seconds",
    [1, 10, 100]
)
def test_timer_valid(seconds):
    request = TimerRequest(seconds=seconds)

    assert request.seconds == seconds


@pytest.mark.parametrize(
    "seconds",
    [0, -1, -100]
)
def test_timer_invalid(seconds):
    with pytest.raises(ValidationError):
        TimerRequest(seconds=seconds)


def test_color_string():
    request = ColorRequest(color="red")

    assert request.color == "red"


def test_color_rgb_tuple():
    request = ColorRequest(
        color=(255, 100, 50)
    )

    assert request.color == (255, 100, 50)


def test_color_xy_tuple():
    request = ColorRequest(
        color=(0.5, 0.4)
    )

    assert request.color == (0.5, 0.4)


@pytest.mark.parametrize(
    "value",
    [-50, -10.5, 0, 10.5, 50]
)
def test_temperature_calibration_valid(value):
    request = TemperatureCalibrationRequest(
        value=value
    )

    assert request.value == value


@pytest.mark.parametrize(
    "value",
    [-50.1, 50.1, -100, 100]
)
def test_temperature_calibration_invalid(value):
    with pytest.raises(ValidationError):
        TemperatureCalibrationRequest(
            value=value
        )


@pytest.mark.parametrize(
    "value",
    [-50, -10.5, 0, 10.5, 50]
)
def test_humidity_calibration_valid(value):
    request = HumidityCalibrationRequest(
        value=value
    )

    assert request.value == value


@pytest.mark.parametrize(
    "value",
    [-50.1, 50.1, -100, 100]
)
def test_humidity_calibration_invalid(value):
    with pytest.raises(ValidationError):
        HumidityCalibrationRequest(
            value=value
        )