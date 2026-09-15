from typing import Annotated

from pydantic import BaseModel, Field


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
