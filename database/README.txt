https://www.prisma.io/dataguide/mongodb/setting-up-a-local-mongodb-database#setting-up-mongodb-on-macos

Start mongodb:
mongod --dbpath ~/ --logpath ~/mongo.log --fork

view a collection:
use sensor_database
use sensor_readings
db.sensor_readings.find()
