int lightPin = 12;
int pumpPin = 11;
int tempPin = A0;
int moisturePin = A1;
int pumpOn = false;
int lightOn = false;

void setup() {
    pinMode(lightPin, OUTPUT);
    pinMode(pumpPin, OUTPUT);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);
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
          int tempRead = analogRead(tempPin);
          int moistureRead = analogRead(moisturePin);
          String sendString = String(tempRead) + "," + String(moistureRead);

          Serial.println(sendString);
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

    delay(1000);
}

