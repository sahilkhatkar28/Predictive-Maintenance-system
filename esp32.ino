
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 2        // Pin where the DHT22 is connected
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define SW420_PIN 5     // Pin where the SW-420 is connected
#define ACS_PIN 21      // Pin where the ACS-712 is connected


// Replace with your network credentials
const char* ssid = "Esp32";
const char* password = "12345678";

// MQTT Broker details
const char* mqtt_server = "mqtt.eclipseprojects.io"; // Corrected broker URL
const int mqtt_port = 1883;

// MQTT Topics
const char* topic_temperature = "diotsensor/temperature";
const char* topic_vibration = "diotsensor/vibration";
const char* topic_current = "diotsensor/current";
const char* topic = "esp32/led";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
const int ledPin = 23; // Built-in LED on most ESP32 boards

void setup() {
  Serial.begin(115200);

  // Start DHT sensor
  dht.begin();

 
  // Initialize the LED pin as an output
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Set up SW-420 pin
  pinMode(SW420_PIN, INPUT);

  // Set up WiFi
  setup_wifi();

  // Set up MQTT
  client.setServer(mqtt_server,mqtt_port);
  client.setCallback(callback);
    // Connect to the MQTT broker
  reconnect();

  // Allow ADC2 (GPIO34) for analogRead
  analogReadResolution(12);

  // Delay to stabilize the system
  delay(1000);
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
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      // Subscribe to LED control topic
      client.subscribe(topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println(message);

  // Control LED based on the message
  if (message == "on") {
    digitalWrite(ledPin, HIGH); // Turn LED on
  } else if (message == "off") {
    digitalWrite(ledPin, LOW); // Turn LED off
  }
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read from DHT22
  float temperature = dht.readTemperature();

  // Read from SW-420
  int vibration = digitalRead(SW420_PIN);

  // Read from ACS-712
  int adcValue = analogRead(ACS_PIN);
  float voltage = (adcValue / 4095.0) * 3.3; // Convert ADC value to voltage
  float current = (voltage - 2.5) / 0.066;  // Convert voltage to current (adjust the formula as per your ACS-712 model)

  // Publish data over MQTT to separate topics
  if (!isnan(temperature)) {
    client.publish(topic_temperature, String(temperature).c_str());
  }
  client.publish(topic_vibration, String(vibration).c_str());
  client.publish(topic_current, String(current).c_str());

  // Debug
  Serial.print("Temperature: ");
  Serial.println(temperature);
  Serial.print("Vibration: ");
  Serial.println(vibration);
  Serial.print("Current: ");
  Serial.println(current);

  delay(5000); // Adjust the delay as needed
}
