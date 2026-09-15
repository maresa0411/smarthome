from fastapi import HTTPException, Request, Depends

from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


def get_home(request: Request) -> SmartHome:
    return request.app.state.home

def _get_light_by_id(light_id: str, home: SmartHome = Depends(get_home)) -> Light:
    light = home.get_device(light_id)
    if light is None or not isinstance(light, Light):
        raise HTTPException(status_code=404, detail="Light not found")
    return light