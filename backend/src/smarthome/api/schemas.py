from datetime import time
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, StrictBool

from smarthome.model.device import Device
from smarthome.model.thermostat import Thermostat


class NewDeviceRequest(BaseModel):
  name: str
  type: str

  @field_validator("type")
  @classmethod
  def validate_type(cls, value: str) -> str:
    normalized = value.lower()
    if normalized not in Device.registry:
      allowed = list(Device.registry.keys())
      raise ValueError(f"Unknown device type '{value}'. Allowed: {allowed}")
    return normalized

# lights
class LightResponse(BaseModel):
    name: str
    is_on: bool | None
    brightness: int | None
    color_temp: int | str | None
    color: dict | None

class ColorTempRequest(BaseModel):
    color_temp: (
        Annotated[int, Field(ge=153, le=500)] | str
    )

class BrightnessRequest(BaseModel):
    value: int = Field(ge=0, le=254)

class TimerRequest(BaseModel):
    seconds: int = Field(gt=0)

class ColorRequest(BaseModel):
    color: str | tuple[int, int, int] | tuple[float, float]

class AlarmRequest(BaseModel):
    start_time: time
    duration: float
    start_brightness: int | None = Field(default=None, ge=0, le=254)
    end_brightness: int | None = Field(default=None, ge=0, le=254)
    color: str | tuple[int, int, int] | tuple[float, float] | None = None

# sensors

class DoorSensorResponse(BaseModel):
    name: str
    closed: bool | None
    battery_low: bool | None
    tamper_proof: bool | None
    battery: float | None
    voltage: float | None

class ClimateSensorResponse(BaseModel):
    name: str
    battery: float | None
    temperature: float | None
    humidity: float | None
    temperature_calibration: float | None
    humidity_calibration: float | None

class TemperatureCalibrationRequest(BaseModel):
    value: float = Field(ge=-50, le=50)

class HumidityCalibrationRequest(BaseModel):
    value: float = Field(ge=-50, le=50)

# -------------------------------------------------------------------
# Response
# -------------------------------------------------------------------

class ThermostatResponse(BaseModel):
    name: str

    local_temperature: float | None = None
    local_temperature_calibration: float | None = None
    occupied_heating_setpoint: float | None = None
    system_mode: str | None = None
    running_state: str | None = None
    battery: int | None = None

    timer_mode_target_temp: float | None = None
    temporary_mode_duration: int | None = None
    temporary_mode: str | None = None

    child_lock: bool | None = None
    open_window: bool | None = None
    smart_temperature_control: bool | None = None

    frost_protection_temperature: float | None = None
    temperature_sensor: str | None = None
    external_temperature_input: float | None = None

    valve_opening_degree: int | None = None
    valve_closing_degree: int | None = None
    temperature_accuracy: float | None = None

    idle_steps: int | None = None
    closing_steps: int | None = None
    valve_opening_limit_voltage: int | None = None
    valve_closing_limit_voltage: int | None = None
    valve_motor_running_voltage: int | None = None


# -------------------------------------------------------------------
# Requests
# -------------------------------------------------------------------

class HeatingSetpointRequest(BaseModel):
    value: float = Field(ge=4, le=35)


class SystemModeRequest(BaseModel):
    mode: Literal["off", "auto", "heat"]


class ThermostatCalibrationRequest(BaseModel):
    value: float = Field(ge=-12.7, le=12.7)


class TimerModeTargetTempRequest(BaseModel):
    value: float = Field(ge=4, le=35)


class TemporaryModeDurationRequest(BaseModel):
    minutes: int = Field(ge=0, le=1440)


class TemporaryModeRequest(BaseModel):
    mode: Literal["boost", "timer"]


class ChildLockRequest(BaseModel):
    locked: StrictBool


class OpenWindowRequest(BaseModel):
    enabled: StrictBool


class SmartTemperatureControlRequest(BaseModel):
    enabled: StrictBool


class FrostProtectionTemperatureRequest(BaseModel):
    value: float = Field(ge=4, le=35)


class TemperatureSensorRequest(BaseModel):
    source: Literal["local_temperature", "remote_temperature"]


class ExternalTemperatureRequest(BaseModel):
    value: float = Field(ge=0, le=99.9)


class ValveDegreeRequest(BaseModel):
    value: int = Field(ge=0, le=100)


class TemperatureAccuracyRequest(BaseModel):
    value: float = Field(ge=-1, le=-0.2)


class WeeklyScheduleRequest(BaseModel):
    # Beispiel: "00:00/18 06:30/21 22:00/18"
    schedule: str

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: str) -> str:
        Thermostat._check_schedule(value)
        return value
