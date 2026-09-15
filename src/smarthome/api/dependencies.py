from fastapi import HTTPException, Request, Depends

from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


def get_home(request: Request) -> SmartHome:
    return request.app.state.home

def _get_light_by_id(light_id: str, home: SmartHome = Depends(get_home)) -> Light:
    light = home.get_device(light_id)
    if light is None or not isinstance(light, Light):
        raise HTTPException(status_code=404, detail="Light not found")
    return light

def _get_door_sensor_by_id(sensor_id: str, home: SmartHome = Depends(get_home)) -> DoorSensor:
    door_sensor = home.get_device(sensor_id)
    if door_sensor is None or not isinstance(door_sensor, DoorSensor):
        raise HTTPException(status_code=404, detail="Door Sensor not found")
    return door_sensor

def _get_climate_sensor_by_id(sensor_id: str, home: SmartHome = Depends(get_home)) -> ClimateSensor:
    climate_sensor = home.get_device(sensor_id)
    if climate_sensor is None or not isinstance(climate_sensor, ClimateSensor):
        raise HTTPException(status_code=404, detail="Climate Sensor not found")
    return climate_sensor