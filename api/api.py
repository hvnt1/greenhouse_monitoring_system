from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
import serial
import serial.tools.list_ports
import uvicorn
import logging
import time
import asyncio

from api.models import SensorReading, Settings, State

CONTROLLER_LOCK = False

# Instantiate the app
app = FastAPI()

# Declare the mongodb config and declare other global variables
client = MongoClient("mongodb://localhost:27017/")
db = client["sensor_database"]
readings = db["sensor_readings"]
settings = db["settings"]
state = db["state"]
controller = None

# Instantiate the logger
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')
logger = logging.getLogger()


@app.on_event("startup")
async def startup_event():
    """Function that will be run on app startup"""

    asyncio.create_task(run_backround_tasks())

async def run_backround_tasks():
    """Function containing tasks to be run continually in the background"""

    while True:
        if controller is not None:
            await sensor_read()
        await asyncio.sleep(1)

@app.get("/")
async def read_root():
    """Endpoint function returning basic info"""

    return {"message": "Greenhouse monitoring system api. Please see /docs for endpoints"}


@app.post("/change_settings")
async def change_settings(request: Request):
    """Endpoint function that changes settings in the db"""

    data = await request.json()
    temp_setting = data['temp_setting']
    moisture_setting = data['moisture_setting']
    operating_mode = data['operating_mode']
    new_settings = Settings(
                    temp_setting=temp_setting,
                    moisture_setting=moisture_setting,
                    operating_mode=operating_mode
                    )
    db["settings"].drop()
    settings.insert_one(new_settings.model_dump())
    return {"message": "settings changed"}


@app.post("/change_state")
async def change_state(request: Request):
    """Endpoint function that changes light and pump state in the db"""

    data = await request.json()
    light = data['light']
    pump = data['pump']
    new_state = State(light=light, pump=pump)
    db["state"].drop()
    state.insert_one(new_state.model_dump())

    await update_controller_state()

    return {"message": "state changed"}


@app.get('/get_readings')
def get_readings():
    """Endpoint function that returns sensor readings from the db"""

    return list(readings.find({}, {'_id': 0}))
    

@app.get('/get_state')
async def get_state():
    """Endpoint function that returns the pump and light state from the db"""

    await update_controller_state()
    read = state.find_one({}, {'_id': 0, 'light': 1, 'pump': 1})
    return State(light=read.get("light"), pump=read.get("pump")).model_dump()


@app.get("/clear_readings")
async def clear_db():
    """Endpoint function that clears all sensor readings in the db"""

    db["sensor_readings"].drop()
    logger.info("Cleared readings table")


async def sensor_read():
    """Function that requests a reading from the controller,
       writes the returned reading to the db, and changes state of the
       light and pump based on the reading"""
    
    global CONTROLLER_LOCK

    if controller:
        while CONTROLLER_LOCK is True:
            await asyncio.sleep(0.1)

        CONTROLLER_LOCK = True
        controller.write("4".encode())
        while controller.in_waiting == 0:
            await asyncio.sleep(0.1)
        line = ''
        controller.readline()
        while True:
            char = controller.read().decode()
            if char == '\n':
                break
            line += char
        controller.flushInput()
        CONTROLLER_LOCK = False
        cont_readings = line.split(',')
        current_time = int(time.time())
        formatted_time = current_time.strftime("%H%M%S")
        if len(cont_readings) == 2 and cont_readings[0] != "1000":
            temp = cont_readings[0]
            moisture = round(int(cont_readings[1]) / 5)
            if moisture > 100:
                moisture = 100

            reading = SensorReading(time=formatted_time, temp=temp, moisture=moisture)

            settings1 = settings.find_one({}, {'_id': 0})
            if settings1.get('operating_mode') == 'Auto':
                states = state.find_one({}, {'_id': 0})
                light = states.get('light')
                pump = states.get('pump')
                if float(temp) < float(settings1.get('temp_setting')):
                    if light == 0:
                        state1 = State(light="1", pump=pump)
                        logger.info("Turned on light")
                        db["state"].drop()
                        state.insert_one(state1.model_dump())
                        controller.write('1'.encode())
                elif light == 1:
                    state1 = State(light="0", pump=pump)
                    logger.info("Turned off light")
                    db["state"].drop()
                    state.insert_one(state1.model_dump())
                    controller.write('0'.encode())
                if float(moisture) < float(settings1.get('moisture_setting')):
                    if pump == 0:
                        state1 = State(light=light, pump="1")
                        logger.info("Turned on pump")
                        db["state"].drop()
                        state.insert_one(state1.model_dump())
                        controller.write('4'.encode())
                elif pump == 1:
                        state1 = State(light=light, pump="0")
                        logger.info("Turned off pump")
                        db["state"].drop()
                        state.insert_one(state1.model_dump())
                        controller.write('3'.encode())

            result = readings.insert_one(reading.model_dump())
            return {'message': 'Sensor reading added successfully',
                    'inserted_id': str(result.inserted_id)}
        else:
            logger.error("Error occured while reading from sensors")


@app.get("/get_settings")
async def get_settings():
    """Endpoint function that returns the settings from the db"""

    fields = settings.find_one({}, {'_id': 0})
    settings1 = Settings(temp_setting=fields.get("temp_setting"), moisture_setting=fields.get("moisture_setting"), operating_mode=fields.get("operating_mode"))
    return settings1.model_dump()


async def update_controller_state():
    """Function that updates the controller light and pump state"""

    global CONTROLLER_LOCK
    states = state.find_one({}, {'_id': 0, 'light': 1, 'pump': 1})
    light = str(states.get('light', '0'))
    pump = str(states.get('pump', '0'))

    while CONTROLLER_LOCK is True:
        await asyncio.sleep(0.1)

    CONTROLLER_LOCK = True  
    if light == '0':
        controller.write('0'.encode())
    elif light == '1':
        controller.write('1'.encode())

    if pump == '0':
        controller.write('2'.encode())
    elif pump == '1':
        controller.write('3'.encode())
    
    await asyncio.sleep(1)
    CONTROLLER_LOCK = False

    logger.info(f"Controller State Updated. Pump: {pump.replace("0", "off").replace("1", "on")}, Light: {light.replace("0", "off").replace("1", "on")}")


def add_default_settings():
    """Function that adds default settings to the db"""
    
    if "settings" not in db.list_collection_names():
        logger.info("Added default settings")
        default_settings = Settings(temp_setting=25.0, moisture_setting=50.0, operating_mode="Auto")
        settings.insert_one(default_settings.model_dump())
    if "state" not in db.list_collection_names():
        logger.info("Added default state")
        default_state = State(light=0, pump=0)
        default_state = default_state.model_dump()
        state.insert_one(default_state)


if __name__ == "__main__":
    logger.info("# Initialising Database")
    add_default_settings()
    logger.info("# Database Initialised")
    logger.info("# Initialising Controller")

    # Connect to Arduino controller serial port
    ports = serial.tools.list_ports.comports()
    controller_port = None
    for port in ports:
        if "usbmodem" in port.device:
            controller_port = port.device
    if controller_port is not None:
        logger.info(f"Successfuly connected to {controller_port}")
        controller = serial.Serial(controller_port, baudrate=9600)
        time.sleep(2)
        asyncio.run(update_controller_state())
        time.sleep(1)
        logger.info("# Controller Initialised")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        logger.error("Failed to connect Arduino controller.")
