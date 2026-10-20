from typing import Literal

from fastapi import APIRouter, Depends

from smarthome.api.dependencies import get_home, _get_thermostat_by_id
from smarthome.api.schemas import (
    ChildLockRequest,
    ExternalTemperatureRequest,
    FrostProtectionTemperatureRequest,
    HeatingSetpointRequest,
    OpenWindowRequest,
    SmartTemperatureControlRequest,
    SystemModeRequest,
    TemperatureAccuracyRequest,
    TemperatureSensorRequest,
    TemporaryModeDurationRequest,
    TemporaryModeRequest,
    ThermostatCalibrationRequest,
    ThermostatResponse,
    TimerModeTargetTempRequest,
    ValveDegreeRequest,
    WeeklyScheduleRequest,
)
from smarthome.model.smart_home import SmartHome
from smarthome.model.thermostat import Thermostat

router = APIRouter(prefix="/thermostats")


# -------------------------------------------------------------------
# read
# -------------------------------------------------------------------

@router.get("", response_model=list[ThermostatResponse])
def get_thermostats(home: SmartHome = Depends(get_home)):
    thermostats = []

    for device in home.devices.values():
        if isinstance(device, Thermostat):
            thermostats.append(_get_thermostat_response(device))

    return thermostats


@router.get("/{thermostat_id}", response_model=ThermostatResponse)
def get_thermostat(
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    return _get_thermostat_response(thermostat)


# -------------------------------------------------------------------
# climate
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/heating_setpoint", status_code=204)
def set_heating_setpoint(
    request: HeatingSetpointRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_heating_setpoint(request.value)


@router.post("/{thermostat_id}/system_mode", status_code=204)
def set_system_mode(
    request: SystemModeRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_system_mode(request.mode)


@router.post("/{thermostat_id}/temperature_calibration", status_code=204)
def set_temperature_calibration(
    request: ThermostatCalibrationRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_local_temperature_calibration(request.value)


# -------------------------------------------------------------------
# temporary mode (boost / timer)
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/timer_mode_target_temp", status_code=204)
def set_timer_mode_target_temp(
    request: TimerModeTargetTempRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_timer_mode_target_temp(request.value)


@router.post("/{thermostat_id}/temporary_mode_duration", status_code=204)
def set_temporary_mode_duration(
    request: TemporaryModeDurationRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_temporary_mode_duration(request.minutes)


@router.post("/{thermostat_id}/temporary_mode", status_code=204)
def set_temporary_mode(
    request: TemporaryModeRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_temporary_mode(request.mode)


# -------------------------------------------------------------------
# switches
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/child_lock", status_code=204)
def set_child_lock(
    request: ChildLockRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_child_lock(request.locked)


@router.post("/{thermostat_id}/open_window", status_code=204)
def set_open_window(
    request: OpenWindowRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_open_window(request.enabled)


@router.post("/{thermostat_id}/smart_temperature_control", status_code=204)
def set_smart_temperature_control(
    request: SmartTemperatureControlRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_smart_temperature_control(request.enabled)


# -------------------------------------------------------------------
# frost protection / temperature source
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/frost_protection_temperature", status_code=204)
def set_frost_protection_temperature(
    request: FrostProtectionTemperatureRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_frost_protection_temperature(request.value)


@router.post("/{thermostat_id}/temperature_sensor", status_code=204)
def set_temperature_sensor(
    request: TemperatureSensorRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_temperature_sensor(request.source)


@router.post("/{thermostat_id}/external_temperature", status_code=204)
def set_external_temperature(
    request: ExternalTemperatureRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_external_temperature(request.value)


# -------------------------------------------------------------------
# valve
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/valve_opening_degree", status_code=204)
def set_valve_opening_degree(
    request: ValveDegreeRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_valve_opening_degree(request.value)


@router.post("/{thermostat_id}/valve_closing_degree", status_code=204)
def set_valve_closing_degree(
    request: ValveDegreeRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_valve_closing_degree(request.value)


@router.post("/{thermostat_id}/temperature_accuracy", status_code=204)
def set_temperature_accuracy(
    request: TemperatureAccuracyRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_temperature_accuracy(request.value)


# -------------------------------------------------------------------
# weekly schedule
# -------------------------------------------------------------------

@router.post("/{thermostat_id}/weekly_schedule/{day}", status_code=204)
def set_weekly_schedule(
    day: Literal[
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ],
    request: WeeklyScheduleRequest,
    thermostat: Thermostat = Depends(_get_thermostat_by_id),
):
    thermostat.set_weekly_schedule(day, request.schedule)


# -------------------------------------------------------------------
# helpers
# -------------------------------------------------------------------

def _get_thermostat_response(thermostat: Thermostat) -> ThermostatResponse:
    return ThermostatResponse(
        name=thermostat.name,
        local_temperature=thermostat.local_temperature,
        local_temperature_calibration=thermostat.local_temperature_calibration,
        occupied_heating_setpoint=thermostat.occupied_heating_setpoint,
        system_mode=thermostat.system_mode,
        running_state=thermostat.running_state,
        battery=thermostat.battery,
        timer_mode_target_temp=thermostat.timer_mode_target_temp,
        temporary_mode_duration=thermostat.temporary_mode_duration,
        temporary_mode=thermostat.temporary_mode,
        child_lock=thermostat.child_lock,
        open_window=thermostat.open_window,
        smart_temperature_control=thermostat.smart_temperature_control,
        frost_protection_temperature=thermostat.frost_protection_temperature,
        temperature_sensor=thermostat.temperature_sensor,
        external_temperature_input=thermostat.external_temperature_input,
        valve_opening_degree=thermostat.valve_opening_degree,
        valve_closing_degree=thermostat.valve_closing_degree,
        temperature_accuracy=thermostat.temperature_accuracy,
        idle_steps=thermostat.idle_steps,
        closing_steps=thermostat.closing_steps,
        valve_opening_limit_voltage=thermostat.valve_opening_limit_voltage,
        valve_closing_limit_voltage=thermostat.valve_closing_limit_voltage,
        valve_motor_running_voltage=thermostat.valve_motor_running_voltage,
    )
