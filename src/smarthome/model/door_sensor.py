from smarthome.model.device import Device


class DoorSensor(Device):
    @property
    def is_closed(self) -> bool | None:
        contact = self.state.get("contact")
        if contact is None:
            return None
        return not contact

    @property
    def is_battery_low(self) -> bool | None:
        return self.state.get("battery_low")

    @property
    def is_tamper_proof(self) -> bool | None:
        tamper = self.state.get("tamper")
        if tamper is None:
            return None
        return not tamper

    @property
    def battery(self) -> int | None:
        return self.state.get("battery")

    @property
    def voltage(self) -> int | None:
        return self.state.get("voltage")