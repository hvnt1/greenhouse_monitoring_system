#include <DHT22.h>

#define lightPin 12
#define pumpPin 11
#define tempPin 2
#define moisturePin A1

int pumpOn = false;
int lightOn = false;

DHT22 dht(tempPin);

void setup() {
    pinMode(lightPin, OUTPUT);
    pinMode(pumpPin, OUTPUT);
    pinMode(moisturePin, INPUT);
    Serial.begin(9600);
}

void loop() {
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
          float tempRead = dht.getTemperature();
          if (dht.getLastError() != dht.OK) {
            Serial.println("1000,1000");
          } else {
            int moistureRead = analogRead(moisturePin);
            String sendString = String(tempRead) + "," + String(moistureRead);
            Serial.println(sendString);
          }
        }

    }

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

