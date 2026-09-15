from smarthome.model.device import Device


class DoorSensor(Device):
    @property
    def is_closed(self):
        return self.state.get("contact") == False

    @property
    def is_battery_low(self):
        return self.state.get("battery_low")

    @property
    def is_tamper_proof(self):
        return self.state.get("tamper") == True

    @property
    def battery(self):
        return self.state.get("battery")

    @property
    def voltage(self):
        return self.state.get("voltage")

    def request_state(self):
        self.get({
            "tamper": "",
            "battery": "",
            "voltage": ""
        })