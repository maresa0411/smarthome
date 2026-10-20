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

import pytest
from pydantic import ValidationError

from smarthome.api.schemas import (
    ChildLockRequest,
    ExternalTemperatureRequest,
    HeatingSetpointRequest,
    SystemModeRequest,
    TemperatureAccuracyRequest,
    TemperatureSensorRequest,
    TemporaryModeDurationRequest,
    TemporaryModeRequest,
    ThermostatCalibrationRequest,
    ThermostatResponse,
    ValveDegreeRequest,
    WeeklyScheduleRequest,
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


@pytest.mark.parametrize("value", [4, 4.5, 21.5, 35])
def test_heating_setpoint_valid(value):
    assert HeatingSetpointRequest(value=value).value == value


@pytest.mark.parametrize("value", [3.9, 35.1, -1, 100])
def test_heating_setpoint_out_of_range(value):
    with pytest.raises(ValidationError):
        HeatingSetpointRequest(value=value)


@pytest.mark.parametrize("value", [-12.7, 0, 12.7])
def test_calibration_valid(value):
    assert ThermostatCalibrationRequest(value=value).value == value


@pytest.mark.parametrize("value", [-12.8, 12.8, -100, 100])
def test_calibration_out_of_range(value):
    with pytest.raises(ValidationError):
        ThermostatCalibrationRequest(value=value)


@pytest.mark.parametrize("value", [0, 99.9])
def test_external_temperature_valid(value):
    assert ExternalTemperatureRequest(value=value).value == value


@pytest.mark.parametrize("value", [-0.1, 99.91])
def test_external_temperature_out_of_range(value):
    with pytest.raises(ValidationError):
        ExternalTemperatureRequest(value=value)


@pytest.mark.parametrize("value", [0, 50, 100])
def test_valve_degree_valid(value):
    assert ValveDegreeRequest(value=value).value == value


@pytest.mark.parametrize("value", [-1, 101, 50.5])
def test_valve_degree_invalid(value):
    with pytest.raises(ValidationError):
        ValveDegreeRequest(value=value)


@pytest.mark.parametrize("value", [-1, -0.6, -0.2])
def test_temperature_accuracy_valid(value):
    assert TemperatureAccuracyRequest(value=value).value == value


@pytest.mark.parametrize("value", [-1.1, -0.1, 0, 1])
def test_temperature_accuracy_invalid(value):
    with pytest.raises(ValidationError):
        TemperatureAccuracyRequest(value=value)


@pytest.mark.parametrize("minutes", [0, 30, 1440])
def test_temporary_mode_duration_valid(minutes):
    assert TemporaryModeDurationRequest(minutes=minutes).minutes == minutes


@pytest.mark.parametrize("minutes", [-1, 1441, 10.5])
def test_temporary_mode_duration_invalid(minutes):
    with pytest.raises(ValidationError):
        TemporaryModeDurationRequest(minutes=minutes)


# -------------------------------------------------------------------
# Auswahlwerte
# -------------------------------------------------------------------

@pytest.mark.parametrize("mode", ["off", "auto", "heat"])
def test_system_mode_valid(mode):
    assert SystemModeRequest(mode=mode).mode == mode


@pytest.mark.parametrize("mode", ["cool", "HEAT", "", None])
def test_system_mode_invalid(mode):
    with pytest.raises(ValidationError):
        SystemModeRequest(mode=mode)


@pytest.mark.parametrize("mode", ["boost", "timer"])
def test_temporary_mode_valid(mode):
    assert TemporaryModeRequest(mode=mode).mode == mode


def test_temporary_mode_invalid():
    with pytest.raises(ValidationError):
        TemporaryModeRequest(mode="turbo")


@pytest.mark.parametrize("source", ["local_temperature", "remote_temperature"])
def test_temperature_sensor_valid(source):
    assert TemperatureSensorRequest(source=source).source == source


@pytest.mark.parametrize("source", ["remote_source_offline", "unknown"])
def test_temperature_sensor_invalid(source):
    with pytest.raises(ValidationError):
        TemperatureSensorRequest(source=source)


# -------------------------------------------------------------------
# Strikte Booleans
# -------------------------------------------------------------------

@pytest.mark.parametrize("value", [True, False])
def test_child_lock_valid(value):
    assert ChildLockRequest(locked=value).locked is value


@pytest.mark.parametrize("value", ["yes", "true", "on", 1, 0, None])
def test_child_lock_rejects_non_booleans(value):
    with pytest.raises(ValidationError):
        ChildLockRequest(locked=value)


# -------------------------------------------------------------------
# Wochenplan
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "schedule",
    [
        "00:00/18",
        "00:00/18 06:30/21 22:00/18",
        "00:00/18 04:00/19 08:00/20 12:00/21 16:00/22 20:00/18",
    ],
)
def test_weekly_schedule_valid(schedule):
    assert WeeklyScheduleRequest(schedule=schedule).schedule == schedule


@pytest.mark.parametrize(
    "schedule",
    [
        "",
        "06:00/20",
        "00:00/18 00:00/19",
        "00:00/18 06:00/20 05:00/21",
        "00:00/3.5",
        "00:00/18.3",
        "00:00/18 24:00/20",
        "00:00-18",
        "00:00/18 03:00/19 06:00/20 09:00/21 12:00/22 15:00/23 18:00/24",
    ],
)
def test_weekly_schedule_invalid(schedule):
    with pytest.raises(ValidationError):
        WeeklyScheduleRequest(schedule=schedule)


def test_weekly_schedule_missing_field():
    with pytest.raises(ValidationError):
        WeeklyScheduleRequest()


# -------------------------------------------------------------------
# Response
# -------------------------------------------------------------------

def test_thermostat_response_defaults_to_none():
    response = ThermostatResponse(name="test_thermostat")

    values = response.model_dump()
    name = values.pop("name")

    assert name == "test_thermostat"
    assert all(value is None for value in values.values())


def test_thermostat_response_requires_name():
    with pytest.raises(ValidationError):
        ThermostatResponse()
