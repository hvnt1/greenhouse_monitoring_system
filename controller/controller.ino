#include <DHT22.h>

// Define constants
#define lightPin 12
#define pumpPin 11
#define tempPin 2
#define moisturePin A1

// Declare global variables
int pumpOn = false;
int lightOn = false;

// Instantiate the dht class
DHT22 dht(tempPin);

// Set pinmodes and begin serial interface
void setup() {
    pinMode(lightPin, OUTPUT);
    pinMode(pumpPin, OUTPUT);
    pinMode(moisturePin, INPUT);
    Serial.begin(9600);
}

// Continuously check if serial data is received and if so then either set
// the state of the light/pump pins or return sensor data via the serial
// interface.
void loop() {
    // Check if serial data is received
    if (Serial.available() > 0)
    {
        char command = Serial.read();
        Serial.println(command);

        if (command == '0')
        {
          lightOn = false;
        }
        else if (command == '1')
        {
          lightOn = true;
        }
        else if (command == '2')
        {
          pumpOn = false;
        }
        else if (command == '3')
        {
          pumpOn = true;
        }
        else if (command == '4')
        {
          while (Serial.available()) {
            Serial.read();  // Read and discard any remaining data in the buffer
          }

          // Get temperature reading
          float tempRead = dht.getTemperature();

          if (dht.getLastError() != dht.OK) {
            // Return error strings so the api can handle
            Serial.println("1000,1000");
          } else {
            // Get moisture reading
            int moistureRead = analogRead(moisturePin);
            // Form string to send from temp and moisture data
            String sendString = String(tempRead) + "," + String(moistureRead);
            //Send the string via serial interface
            Serial.println(sendString);
          }
        }
    }

    // Set state of light and pump pins
    if (pumpOn)
    {
      digitalWrite(pumpPin, HIGH);
    }
    else
    {
      digitalWrite(pumpPin, LOW);
    }

    if (lightOn)
    {
      digitalWrite(lightPin, HIGH);
    }
    else
    {
      digitalWrite(lightPin, LOW);
    }

}

