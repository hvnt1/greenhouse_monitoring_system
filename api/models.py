"""Models used by the API to store and transfer data"""

from pydantic import BaseModel

class SensorReading(BaseModel):
    """Class that stores time, temp and moisture of a sensor reading"""

    time: int
    temp: float
    moisture: float

class Settings(BaseModel):
    """Class that stores temp setting, moisture setting,
       and operating mode"""
    
    temp_setting: float
    moisture_setting: float
    operating_mode: str

class State(BaseModel):
    """Class that stores light and pump state"""
    
    light: int
    pump: int