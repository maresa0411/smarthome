import threading
from datetime import datetime, time, timezone
from typing import TypeAlias

from smarthome.model.device import Device


COLOR_TEMPS = ("coolest", "cool", "neutral", "warm", "warmest")

COLOR_ORANGE = (255, 170, 5)

START_BRIGHTNESS_DEFAULT = 1
END_BRIGHTNESS_DEFAULT = 254

Color: TypeAlias = (
    str
    | tuple[int, int, int]
    | tuple[float, float]
)


class Light(Device):

    def __init__(self, name, mqtt_client):
        super().__init__(name, mqtt_client)

        self._off_timer: threading.Timer | None = None
        self._alarm_thread: threading.Thread | None = None
        self._alarm_stop_event = threading.Event()

    # properties
    @property
    def is_on(self) -> bool | None:
        state = self.state.get("state")

        if state is None:
            return None

        return state == "ON"

    @property
    def brightness(self) -> int | None:
        return self.state.get("brightness")

    @property
    def color_temp(self) -> int | str | None:
        return self.state.get("color_temp")

    @property
    def color(self) -> dict | None:
        return self.state.get("color")

    # state request
    def request_state(self):
        self.get({
            "state": "",
            "brightness": "",
            "color_temp": "",
            "color": ""
        })

    # state
    def toggle_state(self):
        self.set({"state": "TOGGLE"})

    def turn_on(self):
        self.set({"state": "ON"})

    def turn_off(self):
        self.set({"state": "OFF"})

    # brightness
    def set_brightness(self, value: int):
        self._check_brightness(value)

        self.set({
            "brightness": value
        })

    def _check_brightness(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Brightness must be an integer.")

        if not 0 <= value <= 254:
            raise ValueError(
                "Brightness value out of range "
                "(must be between 0 and 254)."
            )

    # color temp
    def set_color_temp(self, color_temp: int | str):

        if isinstance(color_temp, int):
            self._set_color_temp_numeric(color_temp)
            return

        if isinstance(color_temp, str):
            self._set_color_temp_enum(color_temp)
            return

        raise TypeError(
            "color_temp must be an integer or a string."
        )

    def _set_color_temp_numeric(self, color_temp: int):

        if not 153 <= color_temp <= 500:
            raise ValueError(
                "Color temp out of range "
                "(must be between 153 and 500)."
            )

        self.set({
            "color_temp": color_temp
        })

    def _set_color_temp_enum(self, color_temp: str):

        if color_temp not in COLOR_TEMPS:
            raise ValueError(
                "Color temp is not a valid enum value "
                "(must be coolest, cool, neutral, warm, warmest)."
            )

        self.set({
            "color_temp": color_temp
        })

    # color
    def set_color(self, value: Color):

        self._check_color(value)

        if isinstance(value, str):
            self._set_hex_color(value)
            return

        if len(value) == 3:
            self._set_rgb_color(*value)
            return

        self._set_xy_color(*value)

    def _check_color(self, value: Color):

        if isinstance(value, str):
            self._check_hex_color(value)
            return

        if not isinstance(value, tuple):
            raise TypeError(
                "Color must be HEX string, RGB tuple, or XY tuple."
            )

        if len(value) == 3:
            self._check_rgb_color(*value)
            return

        if len(value) == 2:
            self._check_xy_color(*value)
            return

        raise TypeError(
            "Color tuple must contain either 2 or 3 values."
        )

    def _check_hex_color(self, hex_value: str):

        if len(hex_value) != 7:
            raise ValueError(
                "HEX color must have the format #RRGGBB."
            )

        if not hex_value.startswith("#"):
            raise ValueError(
                "HEX color must start with #."
            )

        try:
            int(hex_value[1:], 16)
        except ValueError:
            raise ValueError(
                "HEX color contains invalid characters."
            )

    def _check_rgb_color(self, r: int, g: int, b: int):

        for name, value in (
            ("r", r),
            ("g", g),
            ("b", b),
        ):
            if not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer."
                )

            if not 0 <= value <= 255:
                raise ValueError(
                    f"{name} must be between 0 and 255."
                )

    def _check_xy_color(self, x: float, y: float):

        for name, value in (
            ("x", x),
            ("y", y),
        ):
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be a number."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0."
                )

    def _set_hex_color(self, hex_value: str):

        self.set({
            "color": {
                "hex": hex_value
            }
        })

    def _set_rgb_color(self, r: int, g: int, b: int):

        self.set({
            "color": {
                "r": r,
                "g": g,
                "b": b
            }
        })

    def _set_xy_color(self, x: float, y: float):

        self.set({
            "color": {
                "x": x,
                "y": y
            }
        })

    # timed off
    def turn_on_with_timed_off(self, seconds: int):

        if not isinstance(seconds, int):
            raise TypeError(
                "seconds must be an integer."
            )

        if seconds <= 0:
            raise ValueError(
                "seconds must be > 0."
            )

        if self._off_timer is not None:
            self._off_timer.cancel()

        self.turn_on()

        self._off_timer = threading.Timer(
            seconds,
            self.turn_off
        )

        self._off_timer.daemon = True
        self._off_timer.start()

    # light alarm
    def set_light_alarm(
        self,
        start_time: time,
        duration: float,
        start_brightness: int = START_BRIGHTNESS_DEFAULT,
        end_brightness: int = END_BRIGHTNESS_DEFAULT,
        color: Color = COLOR_ORANGE,
    ) -> None:

        if not isinstance(start_time, time):
            raise TypeError(
                "start_time must be a datetime.time object."
            )

        if not isinstance(duration, (int, float)):
            raise TypeError(
                "duration must be a number."
            )

        if duration <= 0:
            raise ValueError(
                "duration must be greater than 0."
            )

        self._check_brightness(start_brightness)
        self._check_brightness(end_brightness)
        print(f"Color: {color}")
        self._check_color(color)

        if end_brightness < start_brightness:
            raise ValueError(
                "end_brightness must be greater than or equal "
                "to start_brightness."
            )

        self.cancel_light_alarm()

        now = datetime.now(timezone.utc)

        alarm_datetime = datetime.combine(
            now.date(),
            start_time
        )

        print(f"Alarm datetime: {alarm_datetime}")

        if alarm_datetime <= now:
            from datetime import timedelta

            alarm_datetime += timedelta(days=1)

        delay = (
            alarm_datetime - now
        ).total_seconds()

        self._alarm_stop_event.clear()

        self._alarm_thread = threading.Thread(
            target=self._run_light_alarm,
            args=(
                delay,
                duration,
                start_brightness,
                end_brightness,
                color,
            ),
            daemon=True,
        )

        self._alarm_thread.start()

    def _run_light_alarm(
        self,
        delay: float,
        duration: float,
        start_brightness: int,
        end_brightness: int,
        color: Color,
    ) -> None:

        print(f"Wait delay: {delay}")
        if self._alarm_stop_event.wait(delay):
            return

        self.set_brightness(start_brightness)
        self.turn_on()
        self.set_color(color)
        print(self.color)

        self._fade_brightness(
            duration=duration,
            start_brightness=start_brightness,
            end_brightness=end_brightness,
        )

    def _fade_brightness(
        self,
        duration: float,
        start_brightness: int,
        end_brightness: int,
    ) -> None:

        difference = end_brightness - start_brightness

        if difference == 0:
            return

        duration_seconds = duration * 60

        interval = duration_seconds / difference

        for brightness in range(
            start_brightness + 1,
            end_brightness + 1,
        ):

            if self._alarm_stop_event.wait(interval):
                return

            self.set_brightness(brightness)

        self._alarm_thread = None
        print("Alarm finished")

    def cancel_light_alarm(self) -> None:

        self._alarm_stop_event.set()

        self._alarm_thread = None