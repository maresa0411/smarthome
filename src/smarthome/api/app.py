import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome

app = FastAPI()
load_dotenv()
home = SmartHome(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", "1883")))

@app.get("/lights")
def get_lights():
    return

@app.get("/lights/{light_id}")
def get_light(light_id: str):
    light = _get_light_by_id(light_id)
    return {
        "name": light.name,
        "is_on": light.is_on,
        "brightness": light.brightness,
        "color_temp": light.color_temp,
        "color": light.color
    }

@app.post("/lights/{light_id}/turn_on")
def turn_on(light_id: str):
    _get_light_by_id(light_id).turn_on()

@app.post("/lights/{light_id}/turn_off")
def turn_off(light_id: str):
    _get_light_by_id(light_id).turn_off()

@app.post("/lights/{light_id}/toggle")
def toggle(light_id: str):
    _get_light_by_id(light_id).toggle_state()

class BrightnessRequest(BaseModel):
    value: int = Field(ge=0, le=254)

@app.post("/lights/{light_id}/brightness")
def set_brightness(light_id: str, request: BrightnessRequest):
    _get_light_by_id(light_id).set_brightness(request.value)

class ColorTempRequest(BaseModel):
    color_temp: (
        Annotated[int, Field(ge=153, le=500)] | str
    )

@app.post("/lights/{light_id}/color_temp")
def set_color_temp(light_id: str, request: ColorTempRequest):
    _get_light_by_id(light_id).set_color_temp(request.color_temp)

class ColorRequest(BaseModel):
    color: str | tuple[int, int, int] | tuple[float, float]

@app.post("/lights/{light_id}/color")
def set_color(light_id: str, request: ColorRequest):
    _get_light_by_id(light_id).set_color(request.color)

class TimerRequest(BaseModel):
    seconds: int = Field(gt=0)

@app.post("/lights/{light_id}/turn_on_with_timed_off")
def turn_on_with_timed_off(light_id: str, request: TimerRequest):
    _get_light_by_id(light_id).turn_on_with_timed_off(request.seconds)

def _get_light_by_id(light_id: str) -> Light:
    light = home.get_device(light_id)
    if light is None or not isinstance(light, Light):
        raise HTTPException(status_code=404, detail="Light not found")
    return light