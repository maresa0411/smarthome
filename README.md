## SmartHome

A Python-based smart home backend for controlling and monitoring Zigbee devices through MQTT and Zigbee2MQTT.

The project provides a REST API built with FastAPI and abstracts individual Zigbee devices into Python classes. The whole stack (backend, Zigbee2MQTT and Mosquitto) runs as Docker containers, e.g. on a Raspberry Pi.

## Features

Currently supported devices:

* Lights (Currently used model: Nous P3Z)

  * Turn on/off
  * Toggle
  * Set brightness
  * Set color temperature
  * Set HEX, RGB and XY colors
  * Timed turn-off
  * Light alarm (gradual wake-up light with start time, duration, brightness range and color)

* Door sensors (Currently used model: Zigbee Door/Window Sensor)

  * Contact state
  * Battery status
  * Tamper state
  * Voltage

* Climate sensors (Currently used model: Zigbee Temperature and Humidity Sensor)

  * Temperature
  * Humidity
  * Battery status
  * Temperature calibration
  * Humidity calibration

Sensor states are updated through MQTT messages published by Zigbee2MQTT.

Devices are added at runtime through the API and persisted in a `devices.json` file, so they are restored on the next start.

## Architecture

```text
Zigbee devices ── Zigbee dongle ── Zigbee2MQTT ── Mosquitto (MQTT) ── Backend (FastAPI)
                                       │                                     │
                                  Web UI :8080                        REST API :8000
```

| Container           | Image                    | Port | Purpose                                  |
| ------------------- | ------------------------ | ---- | ---------------------------------------- |
| `zigbee2mqtt`       | `koenkk/zigbee2mqtt`     | 8080 | Zigbee bridge and web UI                 |
| `mosquitto`         | `eclipse-mosquitto:2`    | 1883 | MQTT broker                              |
| `smarthome-backend` | built from `./backend`   | 8000 | SmartHome REST API                       |

## Requirements

For the Docker setup:

* Docker with the Compose plugin
* A supported Zigbee USB dongle (currently used: SONOFF Dongle Lite MG21)

For local development:

* Python 3.12+
* An MQTT broker
* Zigbee2MQTT

## Configuration

### Environment variables

| Variable       | Required | Default        | Description                                                                 |
| -------------- | -------- | -------------- | --------------------------------------------------------------------------- |
| `MQTT_HOST`    | yes      | none           | Hostname of the MQTT broker. In Docker: `mosquitto` (the service name).     |
| `MQTT_PORT`    | no       | `1883`         | Port of the MQTT broker.                                                    |
| `DEVICES_FILE` | no       | `devices.json` | Path of the file in which the configured devices are stored.                |
| `TZ`           | no       | system         | Time zone, e.g. `Europe/Berlin`. Needed for correct light alarm start times. |

The light alarm interprets its start time in the local time zone of the machine or container the backend runs on. In Docker, set `TZ`, otherwise the container runs in UTC.

### Local development (`.env`)

Create a `.env` file in the `backend/` directory:

```env
MQTT_HOST=your-mqtt-host
MQTT_PORT=1883
```

Without `DEVICES_FILE`, the devices are stored in `devices.json` in the working directory.

### Docker (`docker-compose.yml`)

The backend is configured through the `environment` section of the compose file. The `DEVICES_FILE` variable points to a mounted volume so that the device list survives rebuilds:

```yaml
  backend:
    build: ./backend
    container_name: smarthome-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./backend-data:/app/data
    environment:
      - TZ=Europe/Berlin
      - MQTT_HOST=mosquitto
      - MQTT_PORT=1883
      - DEVICES_FILE=/app/data/devices.json
    depends_on:
      - mosquitto
```

The device list is then stored on the host in `./backend-data/devices.json`. The directory must exist before the first start (`mkdir -p backend-data`), otherwise Docker creates it owned by `root`.

Without this volume, `devices.json` lives only inside the container and is lost whenever the container is recreated.

### Mosquitto

Mosquitto 2 needs a configuration file in `mosquitto/config/mosquitto.conf`. A minimal example for use inside a trusted local network:

```conf
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
```

For anything exposed beyond your local network, configure authentication instead of `allow_anonymous true`.

### Zigbee2MQTT

Zigbee2MQTT stores its configuration in `zigbee2mqtt/data/`. Make sure the MQTT server in its `configuration.yaml` points to the broker:

```yaml
mqtt:
  server: mqtt://mosquitto:1883
```

The serial device is mapped in `docker-compose.yml` (`devices:`). Adjust the `/dev/serial/by-id/...` path to your dongle.

Pair devices through the Zigbee2MQTT web UI (`http://<host>:8080`). The device name (friendly name) in Zigbee2MQTT must match the name used when adding the device to the backend.

## Running with Docker

Start the whole stack:

```bash
docker compose up -d
```

Check the state of the containers:

```bash
docker compose ps
```

Stop everything:

```bash
docker compose down
```

`down` removes the containers. Data in the mounted directories (`backend-data`, `zigbee2mqtt/data`, `mosquitto/*`) is kept.

### Updating and rebuilding the backend

After pushing changes to the backend, run on the host (in the directory containing `docker-compose.yml`):

```bash
git pull
docker compose up -d --build backend
```

`--build` rebuilds the image from `./backend`, and `up -d` replaces only the backend container. Zigbee2MQTT and Mosquitto keep running. Older Docker installations use `docker-compose` instead of `docker compose`.

Other useful variants:

```bash
# Restart without rebuilding (e.g. after changing environment variables in a .env file)
docker compose restart backend

# Force a fresh container even if nothing changed
docker compose up -d --force-recreate backend

# Rebuild without using the build cache (if a change does not show up)
docker compose build --no-cache backend
docker compose up -d backend
```

### Logs

```bash
# Follow the backend logs (exit with Ctrl+C)
docker compose logs -f backend

# Only the last 100 lines
docker compose logs --tail 100 backend

# Logs of the other services
docker compose logs -f zigbee2mqtt
docker compose logs -f mosquitto

# All services at once
docker compose logs -f
```

Useful for debugging a failed start:

* `Unknown device type` means `devices.json` contains a type the backend does not know.
* Connection errors on startup usually mean the broker is not reachable. Check `MQTT_HOST` and the Mosquitto logs.

### Inspecting the device file

```bash
cat backend-data/devices.json
```

Check that the volume is mounted correctly:

```bash
docker inspect smarthome-backend --format '{{json .Mounts}}'
```

The output must contain an entry with `Destination` `/app/data`. An empty list (`[]`) means the container runs without the volume.

## Running locally (without Docker)

Clone the repository and install the backend including development dependencies:

```bash
pip install -e "backend[dev]"
```

Start the FastAPI application from the `backend` directory:

```bash
cd backend
python -m uvicorn smarthome.api.app:app --app-dir src --port 8000
```

The API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API

Main endpoints are grouped under:

```text
/add_device
/lights
/sensors/doorSensors
/sensors/climateSensors
```

Devices are added with `POST /add_device`. The `type` must be one of `light`, `doorsensor` or `climatesensor`:

```bash
curl -X POST http://localhost:8000/add_device \
  -H "Content-Type: application/json" \
  -d '{"name": "kommode", "type": "light"}'
```

The `name` must match the device name in Zigbee2MQTT. A successful request returns `204` and writes the device to `devices.json`.

The complete API, including request bodies and response schemas, is documented through the FastAPI Swagger UI at `/docs`.

## Tests

Run all tests from the `backend` directory:

```bash
cd backend
pytest
```

The test suite covers the device models, the smart home logic (with a mocked MQTT client and a temporary device file), API dependencies, schemas and REST endpoints. The tests do not need a running broker and do not touch your real `devices.json`.

Coverage reports are generated automatically through `pytest-cov`.

The HTML coverage report can be found at:

```text
backend/htmlcov/index.html
```

Open it, for example, with:

```bash
start htmlcov/index.html
```

## Project Structure

```text
.
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/smarthome/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   ├── app.py
│   │   │   ├── dependencies.py
│   │   │   └── schemas.py
│   │   ├── model/
│   │   │   ├── device.py
│   │   │   ├── smart_home.py
│   │   │   ├── light.py
│   │   │   ├── door_sensor.py
│   │   │   └── climate_sensor.py
│   │   └── main.py
│   └── tests/
│       ├── api/
│       └── model/
├── backend-data/        # devices.json (persistent, not in the image)
├── zigbee2mqtt/data/    # Zigbee2MQTT configuration and network state
└── mosquitto/           # Mosquitto config, data and logs
```

## Tech Stack

* Python
* FastAPI
* Paho MQTT
* Zigbee2MQTT
* Mosquitto
* Docker / Docker Compose
* Pydantic
* pytest
* pytest-cov_

### Disclaimer: This README was generated with Claude.