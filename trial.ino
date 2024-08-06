#include <WiFi.h>
#include <Wire.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ESP32Servo.h> //Servo library
#include <Adafruit_Sensor.h>  // Adafruit sensor library
#include <Adafruit_ADXL345_U.h> // ADXL345 library


/*
====Pin Connections====
ESP32     Servo Motor  |   ESP32     ADXL345    |     ESP32     DHT 22     |     ESP32     Ultrasonic

Vcc       Red          |   3v3       vcc        |     vcc       +          |     Vcc       Vcc
Gnd       Brown        |   Gnd       Gnd        |     Gnd       -          |     Gnd       Gnd
D15       Orange       |   D21       SDA        |     D18       out        |     D5        Trig
***       ***          |   D22       SCL        |                          |     D18       Echo
*/

#define DHTPIN 18       // GPIO pin where the DHT sensor is connected
#define DHTTYPE DHT22    // DHT 11
const int trigPin = 5;   //Triger Pin of Ultrasonic Sensor
const int echoPin = 18;  //Echo Pin of Ultrasonic Sensor
long duration;
Servo myservo;  // Creating servo object to control the servo
const int servoPin = 15; // Servo pin
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(); // ADXL345 Object

const char* ssid = "sensor/data";
const char* password = "12345678";
const char* mqtt_server = "broker.hivemq.com"; // Replace with your MQTT broker address

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  dht.begin();
  //Ultrasonic Sensor Pin Configuration
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myservo.attach(servoPin);
  if (!accel.begin()) {
    Serial.println("ADXL345 not detected");
  }
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float temp = dht.readTemperature();
  float ultra = readUltrasonic();
  float adxl = readadxl();
  int servoPos = myservo.read(); // Read the current servo position

  if (isnan(temp)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  String payload = "Temperature: " + String(temp) + "°C, Distance: " + String(ultra) + "cm, Accelerometer: " + String(adxl) + ", Servo Position: " + String(servoPos);
  Serial.println(payload);

  client.publish("diot/temperature", String(temp).c_str());
  client.publish("diot/ultra", String(ultra).c_str());
  client.publish("diot/adxl", String(adxl).c_str());
  client.publish("diot/servo", String(servoPos).c_str());

  delay(5000); // Wait 2 seconds between readings
}


float readUltrasonic() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);

  // Convert duration to distance in centimeters
  return duration * 0.034 / 2;


}

float readadxl(){
  // Sweep from 0 to 180 degrees
  for (int pos = 0; pos <= 180; pos += 1) {
    sensors_event_t event;
    accel.getEvent(&event);

    myservo.write(pos);  // tell servo to go to position in variable 'pos'
    Serial.print("Servo position: ");
    Serial.println(pos);

    Serial.print("X: ");
    Serial.print(event.acceleration.x);
    Serial.print("  ");
    Serial.print("Y: ");
    Serial.print(event.acceleration.y);
    Serial.print("  ");
    Serial.print("Z: ");
    Serial.print(event.acceleration.z);
    Serial.print("    ");
    delay(5000);  // waits 5000ms for the servo to reach the position
  }
  for (int pos = 180; pos >= 0; pos -= 1) {
    sensors_event_t event;
    accel.getEvent(&event);
    
    myservo.write(pos);  // tell servo to go to position in variable 'pos'
    Serial.print("Servo position: ");
    Serial.println(pos);

    Serial.print("X: ");
    Serial.print(event.acceleration.x);
    Serial.print("  ");
    Serial.print("Y: ");
    Serial.print(event.acceleration.y);
    Serial.print("  ");
    Serial.print("Z: ");
    Serial.print(event.acceleration.z);
    Serial.print("    ");
    delay(5000);  // waits 5000ms for the servo to reach the position
  }

}
