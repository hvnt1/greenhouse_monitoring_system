int ledPin = 13;
int tempPin = A0;
int moisturePin = A1;

void setup() {
    pinMode(ledPin, OUTPUT);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);
    Serial.begin(9600);
}

void loop() {
    int tempRead = analogRead(tempPin);
    int moistureRead = analogRead(moisturePin);
    String sendString = String(tempRead) + "," + String(moistureRead);
    Serial.println(sendString);
    if (Serial.available() > 0)
    {
        char command = Serial.read();
        Serial.println(command);
        if (command == '1')
        {
            digitalWrite(ledPin, HIGH);
        }
        else if (command == '0')
        {
            digitalWrite(ledPin, LOW);
        }
    }
    delay(1000);
}

