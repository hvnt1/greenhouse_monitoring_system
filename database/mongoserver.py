from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["sensor_database"]
readings = db["sensor_readings"]
settings = db["settings"]
state = db["state"]

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

@app.post('/add_reading')
def add_reading(sensor_reading: SensorReading):
    # Insert temperature reading into MongoDB
    sensor_reading = sensor_reading.dict()
    result = readings.insert_one(sensor_reading)
    return {'message': 'Sensor reading added successfully',
            'inserted_id': str(result.inserted_id)}

@app.post('/change_state')
def change_state(new_state: State):
    db["state"].drop()
    new_state = new_state.dict()
    state.insert_one(new_state)
    return {'message' : 'state changed'}

@app.post('/change_settings')
def add_reading(new_settings: Settings):
    db["settings"].drop()
    new_settings = new_settings.dict()
    settings.insert_one(new_settings)
    return {'message' : 'settings changed'}


@app.get('/get_readings')
def get_sensor_readings():
    table = list(readings.find({}, {'_id': 0}))
    return table

@app.get('/get_settings')
def get_settings():
    table = list(settings.find({}, {'_id': 0}))
    return table

@app.get('/get_state')
def get_state():
    table = list(state.find({}, {'_id': 0}))
    return table


@app.get('/clear_readings')
def clear_table():
    db["sensor_readings"].drop()
    return {"message": "cleared table"}

def add_default_settings():
    if "settings" not in db.list_collection_names():
            print("Added default settings")
            default_settings = Settings(temp_setting=25.0, moisture_setting=50.0, operating_mode="Auto")
            default_settings = default_settings.dict()
            settings.insert_one(default_settings)
    if "state" not in db.list_collection_names():
            print("Added default state")
            default_state = State(light=0, pump=0)
            default_state = default_state.dict()
            state.insert_one(default_state)

if __name__ == "__main__":
    add_default_settings()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
