import re

from smarthome.model.device import Device


SYSTEM_MODES = ("off", "auto", "heat")
TEMPORARY_MODES = ("boost", "timer")

SETTABLE_TEMPERATURE_SOURCES = ("local_temperature", "remote_temperature")

WEEKDAYS = (
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
)

TEMP_MIN = 4
TEMP_MAX = 35

CALIBRATION_MIN = -12.7
CALIBRATION_MAX = 12.7

EXTERNAL_TEMP_MIN = 0
EXTERNAL_TEMP_MAX = 99.9

TEMPORARY_DURATION_MIN = 0
TEMPORARY_DURATION_MAX = 1440

ACCURACY_MIN = -1
ACCURACY_MAX = -0.2

MAX_TRANSITIONS_PER_DAY = 6

_TRANSITION_PATTERN = re.compile(r"(\d{2}):(\d{2})/(\d+(?:\.\d+)?)")


class Thermostat(Device):
    """Zigbee radiator thermostat (Sonoff TRVZB)."""

    # ------------------------------------------------------------------
    # properties (read from the published state)
    # ------------------------------------------------------------------

    @property
    def local_temperature(self) -> float | None:
        return self.state.get("local_temperature")

    @property
    def local_temperature_calibration(self) -> float | None:
        return self.state.get("local_temperature_calibration")

    @property
    def occupied_heating_setpoint(self) -> float | None:
        return self.state.get("occupied_heating_setpoint")

    @property
    def system_mode(self) -> str | None:
        return self.state.get("system_mode")

    @property
    def running_state(self) -> str | None:
        return self.state.get("running_state")

    @property
    def battery(self) -> int | None:
        return self.state.get("battery")

    @property
    def timer_mode_target_temp(self) -> float | None:
        return self.state.get("timer_mode_target_temp")

    @property
    def temporary_mode_duration(self) -> int | None:
        return self.state.get("temporary_mode_duration")

    @property
    def temporary_mode(self) -> str | None:
        return self.state.get("temporary_mode_select")

    @property
    def child_lock(self) -> bool | None:
        value = self.state.get("child_lock")

        if value is None:
            return None

        return value == "LOCK"

    @property
    def open_window(self) -> bool | None:
        value = self.state.get("open_window")

        if value is None:
            return None

        return value == "ON"

    @property
    def frost_protection_temperature(self) -> float | None:
        return self.state.get("frost_protection_temperature")

    @property
    def temperature_sensor(self) -> str | None:
        return self.state.get("temperature_sensor_select")

    @property
    def external_temperature_input(self) -> float | None:
        return self.state.get("external_temperature_input")

    @property
    def valve_opening_degree(self) -> int | None:
        return self.state.get("valve_opening_degree")

    @property
    def valve_closing_degree(self) -> int | None:
        return self.state.get("valve_closing_degree")

    @property
    def temperature_accuracy(self) -> float | None:
        return self.state.get("temperature_accuracy")

    @property
    def smart_temperature_control(self) -> bool | None:
        return self.state.get("smart_temperature_control")

    # diagnostic values (read only)
    @property
    def idle_steps(self) -> int | None:
        return self.state.get("idle_steps")

    @property
    def closing_steps(self) -> int | None:
        return self.state.get("closing_steps")

    @property
    def valve_opening_limit_voltage(self) -> int | None:
        return self.state.get("valve_opening_limit_voltage")

    @property
    def valve_closing_limit_voltage(self) -> int | None:
        return self.state.get("valve_closing_limit_voltage")

    @property
    def valve_motor_running_voltage(self) -> int | None:
        return self.state.get("valve_motor_running_voltage")

    # ------------------------------------------------------------------
    # state request
    # ------------------------------------------------------------------

    def request_state(self):
        self.get({
            "local_temperature": "",
            "local_temperature_calibration": "",
            "occupied_heating_setpoint": "",
            "system_mode": "",
            "running_state": "",
            "timer_mode_target_temp": "",
            "temporary_mode_duration": "",
            "temporary_mode_select": "",
            "child_lock": "",
            "open_window": "",
            "frost_protection_temperature": "",
            "temperature_sensor_select": "",
            "external_temperature_input": "",
            "valve_opening_degree": "",
            "valve_closing_degree": "",
            "temperature_accuracy": "",
            "smart_temperature_control": "",
        })

    # ------------------------------------------------------------------
    # climate
    # ------------------------------------------------------------------

    def set_heating_setpoint(self, value: float):
        self._check_number("Heating setpoint", value, TEMP_MIN, TEMP_MAX)

        self.set({"occupied_heating_setpoint": value})

    def set_system_mode(self, mode: str):
        self._check_enum("System mode", mode, SYSTEM_MODES)

        self.set({"system_mode": mode})

    def set_local_temperature_calibration(self, value: float):
        self._check_number(
            "Local temperature calibration",
            value,
            CALIBRATION_MIN,
            CALIBRATION_MAX,
        )

        self.set({"local_temperature_calibration": value})

    # ------------------------------------------------------------------
    # temporary mode (boost / timer)
    # ------------------------------------------------------------------

    def set_timer_mode_target_temp(self, value: float):
        self._check_number(
            "Timer mode target temperature", value, TEMP_MIN, TEMP_MAX
        )

        self.set({"timer_mode_target_temp": value})

    def set_temporary_mode_duration(self, minutes: int):
        self._check_number(
            "Temporary mode duration",
            minutes,
            TEMPORARY_DURATION_MIN,
            TEMPORARY_DURATION_MAX,
            integer=True,
        )

        self.set({"temporary_mode_duration": minutes})

    def set_temporary_mode(self, mode: str):
        self._check_enum("Temporary mode", mode, TEMPORARY_MODES)

        self.set({"temporary_mode_select": mode})

    # ------------------------------------------------------------------
    # switches
    # ------------------------------------------------------------------

    def set_child_lock(self, locked: bool):
        self._check_bool("Child lock", locked)

        self.set({"child_lock": "LOCK" if locked else "UNLOCK"})

    def set_open_window(self, enabled: bool):
        self._check_bool("Open window detection", enabled)

        self.set({"open_window": "ON" if enabled else "OFF"})

    def set_smart_temperature_control(self, enabled: bool):
        self._check_bool("Smart temperature control", enabled)

        self.set({"smart_temperature_control": enabled})

    # ------------------------------------------------------------------
    # frost protection / temperature source
    # ------------------------------------------------------------------

    def set_frost_protection_temperature(self, value: float):
        self._check_number(
            "Frost protection temperature", value, TEMP_MIN, TEMP_MAX
        )

        self.set({"frost_protection_temperature": value})

    def set_temperature_sensor(self, source: str):
        self._check_enum(
            "Temperature sensor", source, SETTABLE_TEMPERATURE_SOURCES
        )

        self.set({"temperature_sensor_select": source})

    def set_external_temperature(self, value: float):
        self._check_number(
            "External temperature",
            value,
            EXTERNAL_TEMP_MIN,
            EXTERNAL_TEMP_MAX,
        )

        self.set({"external_temperature_input": value})

    # ------------------------------------------------------------------
    # valve
    # ------------------------------------------------------------------

    def set_valve_opening_degree(self, value: int):
        self._check_number(
            "Valve opening degree", value, 0, 100, integer=True
        )

        self.set({"valve_opening_degree": value})

    def set_valve_closing_degree(self, value: int):
        self._check_number(
            "Valve closing degree", value, 0, 100, integer=True
        )

        self.set({"valve_closing_degree": value})

    def set_temperature_accuracy(self, value: float):
        self._check_number(
            "Temperature accuracy", value, ACCURACY_MIN, ACCURACY_MAX
        )

        self.set({"temperature_accuracy": value})

    # ------------------------------------------------------------------
    # weekly schedule
    # ------------------------------------------------------------------

    def set_weekly_schedule(self, day: str, schedule: str):
        """Set the heating schedule of one weekday.

        schedule: up to 6 transitions "HH:mm/temperature", separated by
        spaces, e.g. "00:00/18 06:30/21 22:00/18". The first transition
        must start at 00:00.
        """
        self._check_enum("Day", day, WEEKDAYS)
        self._check_schedule(schedule)

        self.set({f"weekly_schedule_{day}": schedule})

    @staticmethod
    def _check_schedule(schedule: str):
        if not isinstance(schedule, str):
            raise TypeError("Schedule must be a string.")

        transitions = schedule.split()

        if not transitions:
            raise ValueError("Schedule must contain at least one transition.")

        if len(transitions) > MAX_TRANSITIONS_PER_DAY:
            raise ValueError(
                f"Schedule can contain at most {MAX_TRANSITIONS_PER_DAY} "
                "transitions per day."
            )

        previous_minutes = -1

        for index, transition in enumerate(transitions):
            match = _TRANSITION_PATTERN.fullmatch(transition)

            if match is None:
                raise ValueError(
                    f"Invalid transition '{transition}' "
                    "(must have the format HH:mm/temperature)."
                )

            hours, minutes, temperature = match.groups()
            hours = int(hours)
            minutes = int(minutes)
            temperature = float(temperature)

            if hours > 23 or minutes > 59:
                raise ValueError(
                    f"Invalid time in transition '{transition}'."
                )

            if not TEMP_MIN <= temperature <= TEMP_MAX:
                raise ValueError(
                    f"Temperature in '{transition}' out of range "
                    f"(must be between {TEMP_MIN} and {TEMP_MAX})."
                )

            if not (temperature * 2).is_integer():
                raise ValueError(
                    f"Temperature in '{transition}' must be "
                    "in steps of 0.5."
                )

            total_minutes = hours * 60 + minutes

            if index == 0 and total_minutes != 0:
                raise ValueError(
                    "The first transition must start at 00:00."
                )

            if total_minutes <= previous_minutes:
                raise ValueError(
                    "Transitions must be in ascending order of time."
                )

            previous_minutes = total_minutes

    # ------------------------------------------------------------------
    # validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_number(
        name: str,
        value,
        minimum: float,
        maximum: float,
        integer: bool = False,
    ):
        # bool ist in Python ein int, soll hier aber nicht durchgehen
        if isinstance(value, bool):
            raise TypeError(f"{name} must be a number.")

        if integer:
            if not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")
        elif not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number.")

        if not minimum <= value <= maximum:
            raise ValueError(
                f"{name} out of range "
                f"(must be between {minimum} and {maximum})."
            )

    @staticmethod
    def _check_enum(name: str, value, allowed: tuple):
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")

        if value not in allowed:
            raise ValueError(
                f"{name} is not valid (must be one of: "
                f"{', '.join(allowed)})."
            )

    @staticmethod
    def _check_bool(name: str, value):
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a boolean.")