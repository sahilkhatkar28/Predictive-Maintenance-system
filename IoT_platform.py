import json
import sqlite3
import paho.mqtt.client as mqtt

# SQLite database initialization
conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS SensorData
             (timestamp INTEGER, name TEXT, temperature REAL, vibration REAL)''')
conn.commit()

class IoTPlatform:
    def __init__(self, broker_address, topic):
        self.client = mqtt.Client()
        self.broker_address = broker_address
        self.topic = topic

        # Connect callback
        self.client.on_connect = self.on_connect
        # Message callback
        self.client.on_message = self.on_message

        # Connect to MQTT broker
        self.client.connect(self.broker_address, 1883)
        # Subscribe to MQTT topic
        self.client.subscribe(self.topic)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        print(f"Received message: {payload}")

        # Parse JSON message
        sensor_data = json.loads(payload)

        # Save data to SQLite database
        timestamp = int(time.time())  # current timestamp
        c.execute("INSERT INTO SensorData VALUES (?, ?, ?, ?)",
                  (timestamp, sensor_data['name'], sensor_data['temperature'], sensor_data['vibration']))
        conn.commit()

    def run(self):
        # Start MQTT client loop to process incoming messages
        self.client.loop_forever()

if __name__ == "__main__":
    platform = IoTPlatform("mqtt.eclipseprojects.io", "industrial/iot")

    try:
        platform.run()

    except KeyboardInterrupt:
        print("Platform stopped by user.")

    finally:
        conn.close()
