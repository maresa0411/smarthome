from fastapi import APIRouter, Depends

from smarthome.api.dependencies import get_home, _get_light_by_id
from smarthome.api.schemas import BrightnessRequest, ColorTempRequest, ColorRequest, LightResponse, TimerRequest, \
    AlarmRequest
from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome

router = APIRouter(prefix="/lights")

@router.get("", response_model=list[LightResponse])
def get_lights(home: SmartHome = Depends(get_home)):
    lights = []

    for device in home.devices.values():
        if isinstance(device, Light):
            lights.append(_get_light_response_to_light(device))

    return lights

@router.get("/{light_id}", response_model=LightResponse)
def get_light(light: Light = Depends(_get_light_by_id)):
    return _get_light_response_to_light(light)

@router.post("/{light_id}/turn_on", status_code=204)
def turn_on(light: Light = Depends(_get_light_by_id)):
    light.turn_on()

@router.post("/{light_id}/turn_off", status_code=204)
def turn_off(light: Light = Depends(_get_light_by_id)):
    light.turn_off()

@router.post("/{light_id}/toggle", status_code=204)
def toggle(light: Light = Depends(_get_light_by_id)):
    light.toggle_state()

@router.post("/{light_id}/brightness", status_code=204)
def set_brightness(request: BrightnessRequest, light: Light = Depends(_get_light_by_id)):
    light.set_brightness(request.value)

@router.post("/{light_id}/color_temp", status_code=204)
def set_color_temp(request: ColorTempRequest, light: Light = Depends(_get_light_by_id)):
    light.set_color_temp(request.color_temp)

@router.post("/{light_id}/color", status_code=204)
def set_color(request: ColorRequest, light: Light = Depends(_get_light_by_id)):
    light.set_color(request.color)

@router.post("/{light_id}/turn_on_with_timed_off", status_code=204)
def turn_on_with_timed_off(request: TimerRequest, light: Light = Depends(_get_light_by_id)):
    light.turn_on_with_timed_off(request.seconds)

@router.post("/{light_id}/set_light_alarm", status_code=204)
def set_light_alarm(
    request: AlarmRequest,
    light: Light = Depends(_get_light_by_id),
):
    print(f"set alarm: {light.name} \n")
    kwargs = {
        "start_time": request.start_time,
        "duration": request.duration,
    }

    if request.start_brightness is not None:
        kwargs["start_brightness"] = request.start_brightness

    if request.end_brightness is not None:
        kwargs["end_brightness"] = request.end_brightness

    if request.color is not None:
        kwargs["color"] = request.color

    print(kwargs)

    light.set_light_alarm(**kwargs)

@router.post("/{light_id}/cancel_light_alarn", status_code=204)
def cancel_light_alarm(light: Light = Depends(_get_light_by_id)):
    print(f"cancel alarm: {light.name}")
    light.cancel_light_alarm()

def _get_light_response_to_light(light: Light) -> LightResponse:
    return LightResponse(
        name=light.name,
        is_on=light.is_on,
        brightness=light.brightness,
        color_temp=light.color_temp,
        color=light.color
    )