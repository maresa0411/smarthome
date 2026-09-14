import os
import time

from dotenv import load_dotenv

from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome


def main():
    load_dotenv()
    smarthome = SmartHome(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", "1883")))

    kommode = Light(
        "kommode",
        smarthome.mqtt_client
    )

    smarthome.add_device(kommode)
    smarthome.start()

    kommode.turn_off()
    time.sleep(2)

    kommode.turn_on_with_timed_off(5)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        smarthome.stop()


if __name__ == "__main__":
    main()