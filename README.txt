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
use sensor_database
db.state.find()

Install requirements:
pip install -r requirements.txt


TODO:
- Fix x axis (times) on graphs
- Smooth temp readings