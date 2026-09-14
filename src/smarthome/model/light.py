import threading

from smarthome.model.device import Device

COLOR_TEMPS = ("coolest", "cool", "neutral", "warm", "warmest")
class Light(Device):
    def __init__(self, name, mqtt_client):
        super().__init__(name, mqtt_client)
        self._off_timer = None
        
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

    # set methods
    def toggle_state(self):
        self.set({"state" : "TOGGLE"})

    def turn_on(self):
        self.set({"state" : "ON"})

    def turn_off(self):
        self.set({"state" : "OFF"})

    def set_brightness(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Brightness must be an integer")
        if value < 0 or value > 254:
            raise ValueError("Brightness value out of range (must be between 0 and 254).")
        self.set({
            "brightness": value
        })

    def set_color_temp(self, color_temp: int | str):
        if isinstance(color_temp, int):
            self._set_color_temp_numeric(color_temp)
            return
        if isinstance(color_temp, str):
            self._set_color_temp_enum(color_temp)
            return

        raise TypeError("color_temp must be an integer or a string")

    def _set_color_temp_numeric(self, color_temp: int):
        if color_temp < 153 or color_temp > 500:
            raise ValueError("Color temp out of range (must be between 153 and 500).")
        self.set({
            "color_temp": color_temp
        })

    def _set_color_temp_enum(self, color_temp: str):
        if color_temp not in COLOR_TEMPS:
            raise ValueError("Color temp ist not a valid enum value (must be coolest, cool, neutral, warm, warmest)")
        self.set({
            "color_temp": color_temp
        })

    def set_color(self, value: str | tuple[int, int, int] | tuple[float, float]):
        if isinstance(value, str):
            self._set_hex_color(value)
            return

        if isinstance(value, tuple) and len(value) == 3:
            self._set_rgb_color(*value)
            return

        if isinstance(value, tuple) and len(value) == 2:
            self._set_xy_color(*value)
            return

        raise TypeError(
            "Color must be HEX string, RGB tuple, or XY tuple."
        )

    def _set_xy_color(self, x: float, y: float):
        for name, value in (("x", x), ("y", y)):
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

        self.set({
            "color": {
                "x": x,
                "y": y
            }
        })

    def _set_rgb_color(self, r: int, g: int, b: int):
        for name, value in (("r", r), ("g", g), ("b", b)):
            if not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")

            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be between 0 and 255")

        self.set({
            "color": {
                "r": r,
                "g": g,
                "b": b
            }
        })

    def _set_hex_color(self, hex_value: str):
        if not isinstance(hex_value, str):
            raise TypeError("hex_value must be a string")

        if len(hex_value) != 7:
            raise ValueError(
                "HEX color must have the format #RRGGBB"
            )

        if not hex_value.startswith("#"):
            raise ValueError(
                "HEX color must start with #"
            )

        try:
            int(hex_value[1:], 16)
        except ValueError:
            raise ValueError(
                "HEX color contains invalid characters"
            )

        self.set({
            "color": {
                "hex": hex_value
            }
        })

    def turn_on_with_timed_off(self, seconds: int):
        if not isinstance(seconds, int):
            raise TypeError("seconds must be an integer.")

        if seconds <= 0:
            raise ValueError("seconds must be > 0.")

        if self._off_timer is not None:
            self._off_timer.cancel()

        self.turn_on()

        self._off_timer = threading.Timer(seconds, self.turn_off)
        self._off_timer.daemon = True
        self._off_timer.start()
    # more options available http://smarthome.local:8080/#/device/0/0xa4c138a23ea8239c/docs
