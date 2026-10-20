import json


class Device:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[cls.__name__.lower()] = cls

    def __init__(self, name, mqtt_client):
        self.name = name
        self.mqtt_client = mqtt_client
        self.topic = f"zigbee2mqtt/{name}"
        self.state = {}

    def set(self, payload: dict):
        self.mqtt_client.publish(
            f"{self.topic}/set",
            json.dumps(payload)
        )

    def get(self, payload: dict):
        self.mqtt_client.publish(
            f"{self.topic}/get",
            json.dumps(payload)
        )

    def on_message(self, payload: dict):
        self.state.update(payload)

    def request_state(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, topic={self.topic!r})"