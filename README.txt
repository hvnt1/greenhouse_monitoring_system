Date group format:
ddmmyyyy

time group format:
hhmmss

https://pythonforthelab.com/blog/how-control-arduino-computer-using-python/

Start venv:
source venv/bin/activate

Start mongodb:
brew services start mongodb-community

Show state in mongodb:
mongosh
use sensor_readings
db.state.find()

Install requirements:
pip3 install -r requirements.txt


TODO:
- raise http exceptions
- Arduino to respond to state update informing success