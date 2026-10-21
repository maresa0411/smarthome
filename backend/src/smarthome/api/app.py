import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from smarthome.api.dependencies import get_home
from smarthome.api.routers import lights, sensors, thermostats
from smarthome.api.schemas import NewDeviceRequest
from smarthome.model.device import Device
from smarthome.model.smart_home import SmartHome

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    home = SmartHome(
        os.getenv("MQTT_HOST"),
        int(os.getenv("MQTT_PORT", "1883")),
        config_file=os.getenv("DEVICES_FILE", "devices.json"),
    )

    app.state.home = home
    home.start()

    try:
        yield
    finally:
        home.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(lights.router)
app.include_router(sensors.router)
app.include_router(thermostats.router)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
   )

@app.post("/add_device", status_code=204)
def add_device(request: NewDeviceRequest, home: SmartHome = Depends(get_home)):
    home.create_and_add_device(request.name, request.type)

@app.delete("/remove_device", status_code=204)
def remove_device(name: str, home: SmartHome = Depends(get_home)):
    try:
        home.remove_device(name)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{name}' not found",
        )

@app.get("/get_device_types")
def get_device_types():
    return Device.registry.keys()