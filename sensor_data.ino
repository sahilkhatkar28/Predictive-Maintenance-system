#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 15      // GPIO pin where the DHT sensor is connected
#define DHTTYPE DHT22  // DHT 11

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

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  String payload = "Temperature: " + String(t) + "°C  Humidity: " + String(h) + "%";
  Serial.println(payload);

  client.publish("sensor/temperature", String(t).c_str());
  client.publish("sensor/humidity", String(h).c_str());

  delay(2000); // Wait 2 seconds between readings
}
