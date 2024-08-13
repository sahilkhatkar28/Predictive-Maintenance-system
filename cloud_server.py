from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import mysql.connector
import paho.mqtt.client as mqtt
from threading import Thread
import logging
import boto3
from botocore.exceptions import ClientError
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# MySQL configuration
db = mysql.connector.connect(
    host="localhost",
    user="iot",       # Replace with your MySQL username
    password="iot",  # Replace with your MySQL password
    database="SensorData"      # Replace with your MySQL database name
)
cursor = db.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    vibration INT,
    current FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Flask app
app = Flask(__name__)
app.secret_key = '12345678'  # Change this to a random secret key

# Simple user credentials
USERNAME = 'iot'
PASSWORD = 'iot'

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials, please try again.'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content and no error

@app.route('/live')
def live_data():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "No data available"}), 404
        
        alert_message = None
        if row[1] > 26:
            alert_message = "Alert: Temperature is above 26°C"
        
        return jsonify({
            "temperature": row[1],
            "vibration": row[2],
            "current": row[3],
            "timestamp": row[4].isoformat(),  # Convert timestamp to ISO format
            "alert": alert_message
        })
    except Exception as e:
        logging.error(f"Error fetching live data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/data')
def show_data():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC")
    data = cursor.fetchall()

    return render_template('data_table.html', data=data)

def send_email_alert(temperature):
    # AWS SES configuration
    sender = 'iotpredictivemaintanance@gmail.com'  # Replace with your verified email address
    recipient = 'sahil7082142712@gmail.com'  # Replace with recipient email address
    subject = "Temperature Alert"
    body_text = f"Alert: The temperature has exceeded 26°C. Current temperature: {temperature}°C"

    # Create a new SES resource
    client = boto3.client('ses', region_name='Asia Pacific (Mumbai)')  # Replace 'your_region' with your AWS SES region (e.g., 'us-east-1')

    try:
        # Send email
        response = client.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [
                    recipient,
                ]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        logging.info(f"Email sent! Message ID: {response['MessageId']}")
    
    except ClientError as e:
        logging.error(f"Failed to send email. Error: {e.response['Error']['Message']}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


# MQTT settings
mqtt_broker = "mqtt.eclipseprojects.io"
mqtt_port = 1883
mqtt_topics = {
    "diotsensor/temperature": "temperature",
    "diotsensor/vibration": "vibration",
    "diotsensor/current": "current"
}
data = {"temperature": None, "vibration": None, "current": None}

def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")
    for topic in mqtt_topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    logging.debug(f"Received message on topic {topic}: {payload}")
    
    if topic in mqtt_topics:
        try:
            data[mqtt_topics[topic]] = float(payload) if mqtt_topics[topic] != "vibration" else int(payload)
            if all(value is not None for value in data.values()):
                cursor.execute("INSERT INTO sensor_data (temperature, vibration, current) VALUES (%s, %s, %s)",
                               (data["temperature"], data["vibration"], data["current"]))
                db.commit()
                logging.info(f"Data inserted: {data}")

                # Check temperature and send email if necessary
                if data["temperature"] > 26:
                    send_email_alert(data["temperature"])
                
                # Reset data to None for next readings
                data["temperature"] = data["vibration"] = data["current"] = None
        except ValueError as e:
            logging.error(f"Error parsing payload: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)

def mqtt_loop():
    client.loop_forever()

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# MQTT setup for LED control
mqtt_client = mqtt.Client()
mqtt_client.connect('mqtt.eclipseprojects.io')

@app.route('/led/<state>', methods=['POST'])
def control_led(state):
    if state not in ['on', 'off']:
        return jsonify({'status': 'error', 'message': 'Invalid state'}), 400

    topic = 'esp32/led'
    payload = {'state': state}

    mqtt_client.publish(topic, json.dumps(payload))

    return jsonify({'status': 'success'})

if __name__ == "__main__":
    Thread(target=mqtt_loop).start()
    Thread(target=run_flask).start()

