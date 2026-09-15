from fastapi import APIRouter, Depends

from smarthome.api.dependencies import get_home, _get_door_sensor_by_id, _get_climate_sensor_by_id
from smarthome.api.schemas import DoorSensorResponse, ClimateSensorResponse
from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.smart_home import SmartHome

router = APIRouter(prefix="/sensors")

@router.get("/doorSensors", response_model=list[DoorSensorResponse])
def get_door_sensors(home: SmartHome = Depends(get_home)):
    door_sensors = []

    for device in home.devices.values():
        if isinstance(device, DoorSensor):
            door_sensors.append(_get_door_sensor_response_to_door_sensor(device))

    return door_sensors

@router.get("/doorSensors/{sensor_id}", response_model=DoorSensorResponse)
def get_door_sensor(door_sensor: DoorSensor = Depends(_get_door_sensor_by_id)):
    return _get_door_sensor_response_to_door_sensor(door_sensor)

@router.get("/climateSensors", response_model=list[ClimateSensorResponse])
def get_climate_sensors(home: SmartHome = Depends(get_home)):
    climate_sensors = []

    for device in home.devices.values():
        if isinstance(device, ClimateSensor):
            climate_sensors.append(_get_climate_sensor_response_to_climate_sensor(device))

    return climate_sensors

@router.get("/climateSensors/{sensor_id}", response_model=ClimateSensorResponse)
def get_climate_sensor(climate_sensor: ClimateSensor = Depends(_get_climate_sensor_by_id)):
    return _get_climate_sensor_response_to_climate_sensor(climate_sensor)

def _get_door_sensor_response_to_door_sensor(door_sensor: DoorSensor) -> DoorSensorResponse:
    return DoorSensorResponse(
        name = door_sensor.name,
        closed = door_sensor.is_closed,
        battery_low = door_sensor.is_battery_low,
        tamper_proof = door_sensor.is_tamper_proof,
        battery = door_sensor.battery,
        voltage = door_sensor.voltage
    )

def _get_climate_sensor_response_to_climate_sensor(climate_sensor: ClimateSensor) -> ClimateSensorResponse:
    return ClimateSensorResponse(
        name = climate_sensor.name,
        battery = climate_sensor.battery,
        temperature = climate_sensor.temperature,
        humidity = climate_sensor.humidity,
        temperature_calibration = climate_sensor.temperature_calibration,
        humidity_calibration = climate_sensor.humidity_calibration
    )