import paho.mqtt.client as mqtt
import mariadb
from mariadb import Error
import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template

# GPIO pin setup
TEMP_LED_PIN = 17  # Temperature LED
STATUS_LED_PIN = 27  # Status LED
BUZZER_PIN = 22     # Buzzer

GPIO.setmode(GPIO.BCM)
GPIO.setup(TEMP_LED_PIN, GPIO.OUT)"""  """
GPIO.setup(STATUS_LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# MQTT details
broker = "mqtt.eclipseprojects.io"
temperature_topic = "diotsensor/temperature"
vibration_topic = "diotsensor/vibration"
current_topic = "diotsensor/current"

# MariaDB connection details
db_config = {
    'host': 'localhost',
    'user': 'your_mariadb_username',
    'password': 'your_mariadb_password',
    'database': 'SensorData'
}

# Flask app initialization
app = Flask(__name__)

# Function to insert data into MariaDB
def insert_data(temperature, vibration, current):
    try:
        connection = mariadb.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO SensorReadings (temperature, vibration, current) VALUES (?, ?, ?)"
        cursor.execute(query, (temperature, vibration, current))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to delete data older than 30 days
def cleanup_old_data():
    try:
        connection = mariadb.connect(**db_config)
        cursor = connection.cursor()
        delete_query = "DELETE FROM SensorReadings WHERE timestamp < NOW() - INTERVAL 30 DAY"
        cursor.execute(delete_query)
        connection.commit()
        print(f"Deleted {cursor.rowcount} records older than 30 days")
    except Error as e:
        print(f"Error during cleanup: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([(temperature_topic, 0), (vibration_topic, 0), (current_topic, 0)])

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received '{payload}' from '{msg.topic}' topic")
    
    if msg.topic == temperature_topic:
        userdata['temperature'] = float(payload)
        # Turn on the temperature LED and buzzer if temperature exceeds 26°C
        if userdata['temperature'] > 26:
            GPIO.output(TEMP_LED_PIN, GPIO.HIGH)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
        else:
            GPIO.output(TEMP_LED_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
    elif msg.topic == vibration_topic:
        userdata['vibration'] = int(payload)
    elif msg.topic == current_topic:
        userdata['current'] = float(payload)

    # Insert data into MariaDB if all values are received
    if None not in (userdata['temperature'], userdata['vibration'], userdata['current']):
        insert_data(userdata['temperature'], userdata['vibration'], userdata['current'])
        cleanup_old_data()  # Clean up old data after each insertion
        userdata['temperature'] = None
        userdata['vibration'] = None
        userdata['current'] = None

# Function to fetch data from MariaDB (last 30 days)
def fetch_data():
    try:
        connection = mariadb.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT * FROM SensorReadings 
            WHERE timestamp >= NOW() - INTERVAL 30 DAY
            ORDER BY timestamp DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Route to display data in table form
@app.route('/')
def index():
    data = fetch_data()
    return render_template('index.html', data=data)

# Function to blink the status LED
def blink_status_led():
    GPIO.output(STATUS_LED_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(STATUS_LED_PIN, GPIO.LOW)
    time.sleep(0.5)

# Flask web server thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Initialize the MQTT client and userdata
client = mqtt.Client(userdata={'temperature': None, 'vibration': None, 'current': None})
client.on_connect = on_connect
client.on_message = on_message

# Main loop
try:
    # Start Flask web server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Connect to the MQTT broker
    client.connect(broker, 1883, 60)

    while True:
        client.loop_start()
        blink_status_led()
        client.loop_stop()
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
