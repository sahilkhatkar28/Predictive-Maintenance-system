import random
import time

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

if __name__ == "__main__":
    equipment = IndustrialEquipment("Machine1")

    try:
        while True:
            equipment.generate_sensor_data()
            sensor_data = equipment.get_sensor_data()
            print(f"Sensor Data: {sensor_data}")
            time.sleep(1)  # Simulate data being generated every second

    except KeyboardInterrupt:
        print("Simulation stopped by user.")
