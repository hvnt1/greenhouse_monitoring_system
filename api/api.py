from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import serial
import requests
import uvicorn
import time
from datetime import datetime

app = FastAPI()

class SensorReading(BaseModel):
    time: int
    temp: float
    moisture: float

class Settings(BaseModel):
    temp_setting: float
    moisture_setting: float
    operating_mode: str

class State(BaseModel):
    light: int
    pump: int

@app.get("/")
async def read_root():
    return {"message": "Greenhouse monitoring system api. Please see /docs for endpoints"}

@app.post("/change_settings")
async def change_settings(request: Request):
    data = await request.json()
    temp_setting = data['temp_setting']
    moisture_setting = data['moisture_setting']
    operating_mode = data['operating_mode']
    settings = Settings(temp_setting=temp_setting, moisture_setting=moisture_setting, operating_mode=operating_mode)
    requests.post('http://localhost:8001/change_settings', json=settings.dict())
    return {"message": "settings changed"}

@app.post("/change_state")
async def change_state(request: Request):
    data = await request.json()
    light = data['light']
    pump = data['pump']
    state = State(light=light, pump=pump)
    requests.post('http://localhost:8001/change_state', json=state.dict())
    updateControllerState()

    return {"message": "state changed"}

@app.get('/get_readings')
def get_readings():
    response = requests.get('http://localhost:8001/get_readings')
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
@app.get('/get_state')
def get_state():
    response = requests.get('http://localhost:8001/get_state')
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/clear_readings")
async def clear_db():
    response = requests.get('http://localhost:8001/clear_readings')
    print(response)

@app.get("/receive_input")
async def sensor_read():
    line = controller.readline().decode().strip()
    controller.flushInput()
    readings = line.split(',')
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H%M%S")
    temp = readings[0]
    moisture = readings[1]
    reading = SensorReading(time=formatted_time, temp=temp, moisture=moisture)

    settings = requests.get('http://localhost:8001/get_settings').text[1:-1].split(",")
    for setting in settings:
        if 'operating_mode' in setting:
            if 'Auto' in setting:
                states = requests.get('http://localhost:8001/get_state').text[1:-1].split(",")
                light = '0'
                pump = '0'
                for state in states:
                    if 'light' in state:
                        light = state[9:]
                    elif 'pump' in state:
                        pump = state[7:-1]
                for setting in settings:
                    if 'temp_setting' in setting:
                        if float(temp) < float(setting[16:]):
                            if light == '0':
                                state = State(light="1", pump=pump)
                                print("Turned on light")
                                requests.post('http://localhost:8001/change_state', json=state.dict())
                                controller.write('1'.encode())
                        else:
                            if light == '1':
                                state = State(light="0", pump=pump)
                                print("Turned off light")
                                requests.post('http://localhost:8001/change_state', json=state.dict())
                                controller.write('0'.encode())
                    elif 'moisture_setting' in setting:
                        if float(moisture) < float(setting[19:]):
                            if pump == '0':
                                state = State(light=light, pump="1")
                                print("Turned on pump")
                                requests.post('http://localhost:8001/change_state', json=state.dict())
                                controller.write('4'.encode())
                        else:
                            if pump == '1':
                                state = State(light=light, pump="0")
                                print("Turned off pump")
                                requests.post('http://localhost:8001/change_state', json=state.dict())
                                controller.write('3'.encode())

    response = requests.post('http://localhost:8001/add_reading', json=reading.dict())
    return {"message": "received reading"}

@app.get("/get_settings")
async def get_settings():
    fields = requests.get('http://localhost:8001/get_settings').text[1:-1].split(",")
    
    for field in fields:
        if 'temp_setting' in field:
            temp_setting = field
        if 'moisture_setting' in field:
            moisture_setting = field
        if 'operating_mode' in field:
            operating_mode = field
    return {'temp_setting': temp_setting, 'moisture_setting': moisture_setting, 'operating_mode': operating_mode}

def updateControllerState():
    states = requests.get('http://localhost:8001/get_state').text[1:-1].split(",")
    light = '0'
    pump = '0'
    for state in states:
        if 'light' in state:
            light = state[9:]
        elif 'pump' in state:
            pump = state[7:-1]

    if light == '0':
        controller.write('0'.encode())
    elif light == '1':
        controller.write('1'.encode())

    if pump == '0':
        controller.write('3'.encode())
    elif pump == '1':
        controller.write('4'.encode())
    print("Cotroller State Updated")

if __name__ == "__main__":
    print("Initialising Controller")
    controller = serial.Serial("/dev/cu.usbmodem1101", baudrate=9600)
    time.sleep(2)
    updateControllerState()
    time.sleep(1)
    uvicorn.run(app, host="127.0.0.1", port=8000)