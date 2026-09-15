import json
import paho.mqtt.client as mqtt

from smarthome.model.device import Device


class SmartHome:
    def __init__(self, mqtt_host: str, mqtt_port: int):
        self.devices = {}
        self.devices_by_topic = {}

        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.connect(mqtt_host, mqtt_port)

    def add_devices(self, *devices: Device):
        for device in devices:
            self.add_device(device)


    def add_device(self, device: Device):
        if device.name in self.devices:
            raise ValueError(
                f"Device '{device.name}' already exists."
            )

        if device.topic in self.devices_by_topic:
            raise ValueError(
                f"Topic '{device.topic}' is already registered."
            )

        self.devices[device.name] = device
        self.devices_by_topic[device.topic] = device

    def remove_device(self, name: str):
        device = self.devices.pop(name)
        self.devices_by_topic.pop(device.topic)

    def get_device(self, name: str):
        return self.devices.get(name)

    def get_device_by_topic(self, topic: str):
        return self.devices_by_topic.get(topic)

    def _on_message(self, client, userdata, msg):
        device = self.get_device_by_topic(msg.topic)

        if device is None:
            return

        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            return

        device.on_message(payload)


    def _on_connect(self, client, userdata, flags, reason_code, properties):
        for device in self.devices.values():
            device.request_state()

    def start(self):
        self.mqtt_client.loop_start()

    def stop(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()