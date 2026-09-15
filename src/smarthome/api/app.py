import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from smarthome.api.routers import lights, sensors
from smarthome.model.climate_sensor import ClimateSensor
from smarthome.model.door_sensor import DoorSensor
from smarthome.model.light import Light
from smarthome.model.smart_home import SmartHome

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(lights.router)
    app.include_router(sensors.router)

    load_dotenv()
    home = SmartHome(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", "1883")))

    kommode = Light("kommode", home.mqtt_client)
    tuer = DoorSensor("tuer_sensor", home.mqtt_client)
    kueche = ClimateSensor("kueche_sensor", home.mqtt_client)
    zimmer = ClimateSensor("zimmer_sensor", home.mqtt_client)

    home.add_devices(kommode, tuer, kueche, zimmer)
    app.state.home = home
    home.start()

    try:
        yield
    finally:
        home.stop()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
   )