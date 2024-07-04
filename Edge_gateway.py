import random
import time
import json
import paho.mqtt.client as mqtt

class IndustrialEquipment:
    def __init__(self, name):
        self.name = name
        self.temperature = 25.0  # Initial temperature
        self.vibration = 0.0  # Initial vibration level

    def generate_sensor_data(self):
        # Simulate temperature fluctuation
        self.temperature += random.uniform(-1.0, 1.0)
        # Simulate vibration level
        self.vibration = random.uniform(0.0, 1.0)

    def get_sensor_data(self):
        return {
            'name': self.name,
            'temperature': self.temperature,
            'vibration': self.vibration
        }

class EdgeGateway:
    def __init__(self, broker_address, topic):
        self.client = mqtt.Client()
        self.broker_address = broker_address
        self.topic = topic

        # Connect callback
        self.client.on_connect = self.on_connect
        # Disconnect callback
        self.client.on_disconnect = self.on_disconnect

        # Connect to MQTT broker
        self.client.connect(self.broker_address, 1883)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker")

    def send_sensor_data(self, sensor_data):
        # Convert sensor data to JSON format
        payload = json.dumps(sensor_data)
        # Publish data to MQTT topic
        self.client.publish(self.topic, payload)
        print(f"Published message: {payload}")

if __name__ == "__main__":
    equipment = IndustrialEquipment("Machine1")
    edge_gateway = EdgeGateway("mqtt.eclipseprojects.io", "industrial/iot")

    try:
        while True:
            equipment.generate_sensor_data()
            sensor_data = equipment.get_sensor_data()
            edge_gateway.send_sensor_data(sensor_data)
            time.sleep(1)  # Simulate data being generated and sent every second

    except KeyboardInterrupt:
        print("Simulation stopped by user.")
