import json
from unittest.mock import Mock

import pytest

from smarthome.model.device import Device
from smarthome.model.thermostat import Thermostat


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def thermostat(mqtt_client):
    return Thermostat("test_thermostat", mqtt_client)


def published(mqtt_client):
    """Topic und Payload des einzigen publish-Aufrufs (Payload als dict)."""
    mqtt_client.publish.assert_called_once()
    topic, payload = mqtt_client.publish.call_args.args

    return topic, json.loads(payload)


# -------------------------------------------------------------------
# Initialization / registry
# -------------------------------------------------------------------

def test_initial_state(thermostat):
    assert thermostat.name == "test_thermostat"
    assert thermostat.topic == "zigbee2mqtt/test_thermostat"
    assert thermostat.state == {}


def test_thermostat_is_registered():
    assert Device.registry["thermostat"] is Thermostat


# -------------------------------------------------------------------
# Properties
# -------------------------------------------------------------------

PROPERTIES = [
    "local_temperature",
    "local_temperature_calibration",
    "occupied_heating_setpoint",
    "system_mode",
    "running_state",
    "battery",
    "timer_mode_target_temp",
    "temporary_mode_duration",
    "temporary_mode",
    "child_lock",
    "open_window",
    "frost_protection_temperature",
    "temperature_sensor",
    "external_temperature_input",
    "valve_opening_degree",
    "valve_closing_degree",
    "temperature_accuracy",
    "smart_temperature_control",
    "idle_steps",
    "closing_steps",
    "valve_opening_limit_voltage",
    "valve_closing_limit_voltage",
    "valve_motor_running_voltage",
]


@pytest.mark.parametrize("name", PROPERTIES)
def test_properties_without_state(thermostat, name):
    assert getattr(thermostat, name) is None


def test_properties(thermostat):
    thermostat.state = {
        "local_temperature": 21.5,
        "local_temperature_calibration": 0.4,
        "occupied_heating_setpoint": 22,
        "system_mode": "heat",
        "running_state": "idle",
        "battery": 88,
        "timer_mode_target_temp": 25,
        "temporary_mode_duration": 30,
        "temporary_mode_select": "boost",
        "child_lock": "LOCK",
        "open_window": "ON",
        "frost_protection_temperature": 7,
        "temperature_sensor_select": "remote_temperature",
        "external_temperature_input": 20.5,
        "valve_opening_degree": 80,
        "valve_closing_degree": 90,
        "temperature_accuracy": -0.4,
        "smart_temperature_control": True,
        "idle_steps": 120,
        "closing_steps": 130,
        "valve_opening_limit_voltage": 1500,
        "valve_closing_limit_voltage": 1400,
        "valve_motor_running_voltage": 1300,
    }

    assert thermostat.local_temperature == 21.5
    assert thermostat.local_temperature_calibration == 0.4
    assert thermostat.occupied_heating_setpoint == 22
    assert thermostat.system_mode == "heat"
    assert thermostat.running_state == "idle"
    assert thermostat.battery == 88
    assert thermostat.timer_mode_target_temp == 25
    assert thermostat.temporary_mode_duration == 30
    assert thermostat.temporary_mode == "boost"
    assert thermostat.child_lock is True
    assert thermostat.open_window is True
    assert thermostat.frost_protection_temperature == 7
    assert thermostat.temperature_sensor == "remote_temperature"
    assert thermostat.external_temperature_input == 20.5
    assert thermostat.valve_opening_degree == 80
    assert thermostat.valve_closing_degree == 90
    assert thermostat.temperature_accuracy == -0.4
    assert thermostat.smart_temperature_control is True
    assert thermostat.idle_steps == 120
    assert thermostat.closing_steps == 130
    assert thermostat.valve_opening_limit_voltage == 1500
    assert thermostat.valve_closing_limit_voltage == 1400
    assert thermostat.valve_motor_running_voltage == 1300


def test_child_lock_unlocked_is_false(thermostat):
    thermostat.state = {"child_lock": "UNLOCK"}

    assert thermostat.child_lock is False


def test_open_window_off_is_false(thermostat):
    thermostat.state = {"open_window": "OFF"}

    assert thermostat.open_window is False


def test_smart_temperature_control_false(thermostat):
    thermostat.state = {"smart_temperature_control": False}

    assert thermostat.smart_temperature_control is False


def test_on_message_updates_properties(thermostat):
    thermostat.on_message({"local_temperature": 19.5, "battery": 70})

    assert thermostat.local_temperature == 19.5
    assert thermostat.battery == 70


# -------------------------------------------------------------------
# request_state
# -------------------------------------------------------------------

def test_request_state(thermostat, mqtt_client):
    thermostat.request_state()

    topic, payload = published(mqtt_client)

    assert topic == "zigbee2mqtt/test_thermostat/get"
    assert "local_temperature" in payload
    assert "occupied_heating_setpoint" in payload
    assert "system_mode" in payload
    assert "running_state" in payload

    # alle Werte sind leer (Zigbee2MQTT erwartet "" bei /get)
    assert set(payload.values()) == {""}


def test_request_state_skips_values_that_cannot_be_read(
    thermostat, mqtt_client
):
    thermostat.request_state()

    _, payload = published(mqtt_client)

    assert "battery" not in payload
    assert not any(key.startswith("weekly_schedule") for key in payload)


# -------------------------------------------------------------------
# Setters: gueltige Werte
# -------------------------------------------------------------------

VALID = [
    ("set_heating_setpoint", 4, {"occupied_heating_setpoint": 4}),
    ("set_heating_setpoint", 21.5, {"occupied_heating_setpoint": 21.5}),
    ("set_heating_setpoint", 35, {"occupied_heating_setpoint": 35}),

    ("set_system_mode", "off", {"system_mode": "off"}),
    ("set_system_mode", "auto", {"system_mode": "auto"}),
    ("set_system_mode", "heat", {"system_mode": "heat"}),

    ("set_local_temperature_calibration", -12.7,
     {"local_temperature_calibration": -12.7}),
    ("set_local_temperature_calibration", 0,
     {"local_temperature_calibration": 0}),
    ("set_local_temperature_calibration", 12.7,
     {"local_temperature_calibration": 12.7}),

    ("set_timer_mode_target_temp", 4, {"timer_mode_target_temp": 4}),
    ("set_timer_mode_target_temp", 35, {"timer_mode_target_temp": 35}),

    ("set_temporary_mode_duration", 0, {"temporary_mode_duration": 0}),
    ("set_temporary_mode_duration", 1440, {"temporary_mode_duration": 1440}),

    ("set_temporary_mode", "boost", {"temporary_mode_select": "boost"}),
    ("set_temporary_mode", "timer", {"temporary_mode_select": "timer"}),

    ("set_child_lock", True, {"child_lock": "LOCK"}),
    ("set_child_lock", False, {"child_lock": "UNLOCK"}),

    ("set_open_window", True, {"open_window": "ON"}),
    ("set_open_window", False, {"open_window": "OFF"}),

    ("set_smart_temperature_control", True,
     {"smart_temperature_control": True}),
    ("set_smart_temperature_control", False,
     {"smart_temperature_control": False}),

    ("set_frost_protection_temperature", 4,
     {"frost_protection_temperature": 4}),
    ("set_frost_protection_temperature", 35,
     {"frost_protection_temperature": 35}),

    ("set_temperature_sensor", "local_temperature",
     {"temperature_sensor_select": "local_temperature"}),
    ("set_temperature_sensor", "remote_temperature",
     {"temperature_sensor_select": "remote_temperature"}),

    ("set_external_temperature", 0, {"external_temperature_input": 0}),
    ("set_external_temperature", 99.9, {"external_temperature_input": 99.9}),

    ("set_valve_opening_degree", 0, {"valve_opening_degree": 0}),
    ("set_valve_opening_degree", 100, {"valve_opening_degree": 100}),

    ("set_valve_closing_degree", 0, {"valve_closing_degree": 0}),
    ("set_valve_closing_degree", 100, {"valve_closing_degree": 100}),

    ("set_temperature_accuracy", -1, {"temperature_accuracy": -1}),
    ("set_temperature_accuracy", -0.2, {"temperature_accuracy": -0.2}),
]


@pytest.mark.parametrize("method, value, expected", VALID)
def test_setter_publishes_payload(
    thermostat, mqtt_client, method, value, expected
):
    getattr(thermostat, method)(value)

    topic, payload = published(mqtt_client)

    assert topic == "zigbee2mqtt/test_thermostat/set"
    assert payload == expected


# -------------------------------------------------------------------
# Setters: Wert ausserhalb des Bereichs / ungueltiger Wert
# -------------------------------------------------------------------

OUT_OF_RANGE = [
    ("set_heating_setpoint", 3.9),
    ("set_heating_setpoint", 35.1),
    ("set_heating_setpoint", -10),

    ("set_system_mode", "cool"),
    ("set_system_mode", "OFF"),
    ("set_system_mode", ""),

    ("set_local_temperature_calibration", -12.8),
    ("set_local_temperature_calibration", 12.8),

    ("set_timer_mode_target_temp", 3.9),
    ("set_timer_mode_target_temp", 35.1),

    ("set_temporary_mode_duration", -1),
    ("set_temporary_mode_duration", 1441),

    ("set_temporary_mode", "turbo"),
    ("set_temporary_mode", ""),

    ("set_frost_protection_temperature", 3.9),
    ("set_frost_protection_temperature", 35.1),

    # wird vom Geraet gemeldet, nicht gesetzt
    ("set_temperature_sensor", "remote_source_offline"),
    ("set_temperature_sensor", "unknown"),

    ("set_external_temperature", -0.1),
    ("set_external_temperature", 99.91),

    ("set_valve_opening_degree", -1),
    ("set_valve_opening_degree", 101),

    ("set_valve_closing_degree", -1),
    ("set_valve_closing_degree", 101),

    ("set_temperature_accuracy", -1.1),
    ("set_temperature_accuracy", -0.1),
    ("set_temperature_accuracy", 0),
]


@pytest.mark.parametrize("method, value", OUT_OF_RANGE)
def test_setter_out_of_range_raises_value_error(
    thermostat, mqtt_client, method, value
):
    with pytest.raises(ValueError):
        getattr(thermostat, method)(value)

    mqtt_client.publish.assert_not_called()


# -------------------------------------------------------------------
# Setters: falscher Typ
# -------------------------------------------------------------------

WRONG_TYPE = [
    ("set_heating_setpoint", "21"),
    ("set_heating_setpoint", None),
    ("set_heating_setpoint", True),

    ("set_system_mode", None),
    ("set_system_mode", 1),

    ("set_local_temperature_calibration", "1"),
    ("set_local_temperature_calibration", None),
    ("set_local_temperature_calibration", True),

    ("set_timer_mode_target_temp", "10"),
    ("set_timer_mode_target_temp", None),

    ("set_temporary_mode_duration", 10.5),
    ("set_temporary_mode_duration", "10"),
    ("set_temporary_mode_duration", None),
    ("set_temporary_mode_duration", True),

    ("set_temporary_mode", None),
    ("set_temporary_mode", 1),

    ("set_child_lock", 1),
    ("set_child_lock", "yes"),
    ("set_child_lock", None),

    ("set_open_window", 0),
    ("set_open_window", "ON"),
    ("set_open_window", None),

    ("set_smart_temperature_control", 1),
    ("set_smart_temperature_control", None),

    ("set_frost_protection_temperature", "5"),
    ("set_frost_protection_temperature", None),

    ("set_temperature_sensor", None),
    ("set_temperature_sensor", 1),

    ("set_external_temperature", "5"),
    ("set_external_temperature", None),

    ("set_valve_opening_degree", 50.5),
    ("set_valve_opening_degree", "50"),
    ("set_valve_opening_degree", None),

    ("set_valve_closing_degree", 50.5),
    ("set_valve_closing_degree", "50"),
    ("set_valve_closing_degree", None),

    ("set_temperature_accuracy", "-1"),
    ("set_temperature_accuracy", None),
]


@pytest.mark.parametrize("method, value", WRONG_TYPE)
def test_setter_wrong_type_raises_type_error(
    thermostat, mqtt_client, method, value
):
    with pytest.raises(TypeError):
        getattr(thermostat, method)(value)

    mqtt_client.publish.assert_not_called()


# -------------------------------------------------------------------
# Weekly schedule
# -------------------------------------------------------------------

DAYS = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]


@pytest.mark.parametrize("day", DAYS)
def test_weekly_schedule_publishes_for_each_day(
    thermostat, mqtt_client, day
):
    thermostat.set_weekly_schedule(day, "00:00/18 06:30/21 22:00/18")

    topic, payload = published(mqtt_client)

    assert topic == "zigbee2mqtt/test_thermostat/set"
    assert payload == {f"weekly_schedule_{day}": "00:00/18 06:30/21 22:00/18"}


@pytest.mark.parametrize(
    "schedule",
    [
        "00:00/18",
        "00:00/18.5",
        "00:00/4 12:00/35",
        "00:00/18 23:59/20",
        # genau 6 Uebergaenge
        "00:00/18 04:00/19 08:00/20 12:00/21 16:00/22 20:00/18",
    ],
)
def test_weekly_schedule_valid(thermostat, mqtt_client, schedule):
    thermostat.set_weekly_schedule("monday", schedule)

    _, payload = published(mqtt_client)

    assert payload == {"weekly_schedule_monday": schedule}


@pytest.mark.parametrize(
    "schedule",
    [
        "",
        "   ",
        # erster Uebergang nicht um 00:00
        "06:00/20",
        # mehr als 6 Uebergaenge
        "00:00/18 03:00/19 06:00/20 09:00/21 12:00/22 15:00/23 18:00/24",
        # Temperatur ausserhalb 4-35
        "00:00/3.5",
        "00:00/35.5",
        # keine 0,5-Schritte
        "00:00/18.3",
        # Zeiten nicht aufsteigend / doppelt
        "00:00/18 00:00/20",
        "00:00/18 06:00/20 05:00/21",
        # ungueltige Uhrzeit
        "00:00/18 24:00/20",
        "00:00/18 12:60/20",
        # falsches Format
        "0:00/18",
        "00:00-18",
        "00:00/18,06:00/20",
        "00:00/abc",
        "00:00",
        "/18",
    ],
)
def test_weekly_schedule_invalid_raises_value_error(
    thermostat, mqtt_client, schedule
):
    with pytest.raises(ValueError):
        thermostat.set_weekly_schedule("monday", schedule)

    mqtt_client.publish.assert_not_called()


@pytest.mark.parametrize("schedule", [None, 18, ["00:00/18"]])
def test_weekly_schedule_invalid_type_raises_type_error(
    thermostat, mqtt_client, schedule
):
    with pytest.raises(TypeError):
        thermostat.set_weekly_schedule("monday", schedule)

    mqtt_client.publish.assert_not_called()


@pytest.mark.parametrize("day", ["funday", "Monday", "mon", ""])
def test_weekly_schedule_invalid_day_raises_value_error(
    thermostat, mqtt_client, day
):
    with pytest.raises(ValueError):
        thermostat.set_weekly_schedule(day, "00:00/18")

    mqtt_client.publish.assert_not_called()


@pytest.mark.parametrize("day", [None, 1])
def test_weekly_schedule_invalid_day_type_raises_type_error(
    thermostat, mqtt_client, day
):
    with pytest.raises(TypeError):
        thermostat.set_weekly_schedule(day, "00:00/18")

    mqtt_client.publish.assert_not_called()
