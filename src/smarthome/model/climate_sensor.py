from smarthome.model.device import Device


class ClimateSensor(Device):
    # properties
    @property
    def battery(self) -> int | None:
        return self.state.get("battery")

    @property
    def temperature(self) -> float | None:
        return self.state.get("temperature")

    @property
    def humidity(self) -> float | None:
        return self.state.get("humidity")

    @property
    def temperature_calibration(self) -> float | None:
        return self.state.get("temperature_calibration")

    @property
    def humidity_calibration(self) -> float | None:
        return self.state.get("humidity_calibration")

    def request_state(self):
        self.get({
            "battery": "",
            "temperature": "",
            "humidity": "",
            "temperature_calibration": "",
            "humidity_calibration": ""
        })

    # set methods
    def set_temperature_calibration(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "Temperature calibration must be numeric."
            )

        if not -50 <= value <= 50:
            raise ValueError(
                "Temperature calibration must be between -50 and 50."
            )

        self.set({
            "temperature_calibration": value
        })

    def set_humidity_calibration(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "Humidity calibration must be numeric."
            )

        if not -50 <= value <= 50:
            raise ValueError(
                "Humidity calibration must be between -50 and 50."
            )

        self.set({
            "humidity_calibration": value
        })
