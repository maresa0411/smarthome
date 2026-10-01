from datetime import time
from typing import Annotated

from pydantic import BaseModel, Field

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
