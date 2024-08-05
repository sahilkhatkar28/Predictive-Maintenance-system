#include <Wire.h>
#include <Adafruit_Sensor.h>  // Adafruit sensor library
#include <Adafruit_ADXL345_U.h> // ADXL345 library

Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(); // ADXL345 Object

/*
====Pin Connections====
ESP32     ADXL345
3v3       vcc
Gnd       Gnd
D21       SDA
D22       SCL
*/

void setup() {
  Serial.begin(9600);
  
  // Check if the sensor is detected
  if (!accel.begin()) {
    Serial.println("ADXL345 not detected");
    while (1); // Stop the program if sensor is not found
  }
}

void loop() {
  sensors_event_t event;
  accel.getEvent(&event);

  // Print acceleration values
  Serial.print("X: ");
  Serial.print(event.acceleration.x);
  Serial.print("  ");
  Serial.print("Y: ");
  Serial.print(event.acceleration.y);
  Serial.print("  ");
  Serial.print("Z: ");
  Serial.print(event.acceleration.z);
  Serial.println(" m/s^2");

  delay(500);
}
