import os

from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


def main():
    smarthome = SmartHome(os.getenv("MQTT_HOST", os.getenv("MQTT_PORT")))

    kommode = Light("kommode", smarthome.mqtt_client, "zigbee2mqtt/kommode")

    smarthome.add_device(kommode)

    smarthome.start()


if __name__ == "__main__":
    main()