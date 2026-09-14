import json


class Device:

    def __init__(self, name, mqtt_client, topic):
        self.name = name
        self.mqtt_client = mqtt_client
        self.topic = topic
        self.state = {}

        self.mqtt_client.subscribe(self.topic)

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

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, topic={self.topic!r})"