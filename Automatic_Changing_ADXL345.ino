#include <Wire.h>
#include <ESP32Servo.h> //Servo library
#include <Adafruit_Sensor.h>  // Adafruit sensor library
#include <Adafruit_ADXL345_U.h> // ADXL345 library

/*_****Servo and ADXL objects****_*/

Servo myservo;  // Creating servo object to control the servo
const int servoPin = 13; // Servo pin

Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(); // ADXL345 Object


/*
====Pin Connections====
ESP32     Servo Motor  |   ESP32     ADXL345

Vcc       Red          |   3v3       vcc
Gnd       Brown        |   Gnd       Gnd
D13       Orange       |   D21       SDA
***       ***          |   D22       SCL
*/

void setup() {
  Serial.begin(9600);
  myservo.attach(servoPin);
  
  // Check if the ADXL sensor is detected
  if (!accel.begin()) {
    Serial.println("ADXL345 not detected");
    while (1); // Stop the program if sensor is not found
  }
}

void loop() {

  // Sweep from 0 to 180 degrees
  for (int pos = 0; pos <= 180; pos += 1) {
    sensors_event_t event;
    accel.getEvent(&event);

    myservo.write(pos);  // tell servo to go to position in variable 'pos'
    Serial.print("Servo position: ");
    Serial.println(pos);

    Serial.print("X: ");
    Serial.print(event.acceleration.x);
    Serial.print("  ");
    Serial.print("Y: ");
    Serial.print(event.acceleration.y);
    Serial.print("  ");
    Serial.print("Z: ");
    Serial.print(event.acceleration.z);
    Serial.print("    ");
    delay(500);  // waits 500ms for the servo to reach the position
  }
  for (int pos = 180; pos >= 0; pos -= 1) {
    sensors_event_t event;
    accel.getEvent(&event);
    
    myservo.write(pos);  // tell servo to go to position in variable 'pos'
    Serial.print("Servo position: ");
    Serial.println(pos);

    Serial.print("X: ");
    Serial.print(event.acceleration.x);
    Serial.print("  ");
    Serial.print("Y: ");
    Serial.print(event.acceleration.y);
    Serial.print("  ");
    Serial.print("Z: ");
    Serial.print(event.acceleration.z);
    Serial.print("    ");
    delay(500);  // waits 500ms for the servo to reach the position
  }
}
