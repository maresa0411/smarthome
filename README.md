# SmartHome

A Python-based smart home backend for controlling and monitoring Zigbee devices through MQTT and Zigbee2MQTT.

The project provides a REST API built with FastAPI and abstracts individual Zigbee devices into Python classes.

## Features

Currently supported devices:

* Lights (Currently used model: Nous P3Z)

  * Turn on/off
  * Toggle
  * Set brightness
  * Set color temperature
  * Set HEX, RGB and XY colors
  * Timed turn-off
  
* Door sensors (Currently used model: Zigbee Temperature and Humidity Sensor)

  * Contact state
  * Battery status
  * Tamper state
  * Voltage
  
* Climate sensors (Currently used model: Zigbee Door/Window Sensor)

  * Temperature
  * Humidity
  * Battery status
  * Temperature calibration
  * Humidity calibration

Sensor states are updated through MQTT messages published by Zigbee2MQTT.

## Requirements

* Python 3.12+
* MQTT broker
* Zigbee2MQTT

## Installation

Clone the repository and install the project including development dependencies:

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root:

```env
MQTT_HOST=your-mqtt-host
MQTT_PORT=1883
```

The configured Zigbee2MQTT device names must match the names used by the application.

## Running the API

Start the FastAPI application with:

```bash
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
/lights
/sensors/doorSensors
/sensors/climateSensors
```

The complete API, including request bodies and response schemas, is documented through the FastAPI Swagger UI at `/docs`.

## Tests

Run all tests with:

```bash
pytest
```

The test suite covers the device models, MQTT-independent smart home logic, API dependencies, schemas and REST endpoints.

Coverage reports are generated automatically through `pytest-cov`.

The HTML coverage report can be found at:

```text
htmlcov/index.html
```
via

```bash
start htmlcov/index.html
```

## Project Structure

```text
src/smarthome/
├── api/
│   ├── routers/
│   ├── app.py
│   ├── dependencies.py
│   └── schemas.py
└── model/
    ├── device.py
    ├── smart_home.py
    ├── light.py
    ├── door_sensor.py
    └── climate_sensor.py

tests/
├── api/
└── model/
```

## Tech Stack

* Python
* FastAPI
* Paho MQTT
* Zigbee2MQTT
* Pydantic
* pytest
* pytest-cov
