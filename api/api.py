from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import serial
import requests
import uvicorn
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
    readings = line.split(',')
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H%M%S")
    reading = SensorReading(time=formatted_time, temp=readings[0], moisture=readings[1])
    print("Added to database:",reading)
    response = requests.post('http://localhost:8001/add_reading', json=reading.dict())
    return {"message": "received reading"}

@app.get("/light_on")
async def light_on():
    controller.write('1'.encode())
    line = controller.readline().decode().strip()
    return line

@app.get("/light_off")
async def light_off():
    controller.write('0'.encode())

@app.get("/pump_on")
async def pump_on():
    controller.write('4'.encode())

@app.get("/pump_off")
async def pump_off():
    controller.write('3'.encode())

@app.get("/get_settings")
async def get_settings():
    response = requests.get('http://localhost:8001/get_settings')
    response_body = response.text
    response_body = response_body[1:-1]
    fields = response_body.split(",")
    
    for field in fields:
        if 'temp_setting' in field:
            temp_setting = field
        if 'moisture_setting' in field:
            moisture_setting = field
        if 'operating_mode' in field:
            operating_mode = field
    return {'temp_setting': temp_setting, 'moisture_setting': moisture_setting, 'operating_mode': operating_mode}

if __name__ == "__main__":
    controller = serial.Serial("/dev/cu.usbmodem1101", baudrate=9600)
    uvicorn.run(app, host="127.0.0.1", port=8000)