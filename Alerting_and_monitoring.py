import sqlite3
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SQLite database initialization
conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()

# Example email configuration (replace with your SMTP server details)
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_email@example.com'
SMTP_PASSWORD = 'your_password'
EMAIL_FROM = 'your_email@example.com'
EMAIL_TO = 'recipient@example.com'

# Function to send email alerts
def send_email_alert(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print("Email alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email alert: {str(e)}")

# Example monitoring function
def monitor_sensor_data():
    while True:
        c.execute("SELECT * FROM SensorData ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()

        if row:
            timestamp, name, temperature, vibration = row
            # Example thresholds for temperature and vibration
            if temperature > 30.0:
                subject = f"High Temperature Alert ({name})"
                message = f"Temperature exceeded threshold (30.0°C): {temperature}°C at {time.ctime(timestamp)}"
                send_email_alert(subject, message)

            if vibration > 0.8:
                subject = f"High Vibration Alert ({name})"
                message = f"Vibration exceeded threshold (0.8): {vibration} at {time.ctime(timestamp)}"
                send_email_alert(subject, message)

        time.sleep(10)  # Adjust interval as needed

if __name__ == "__main__":
    try:
        monitor_sensor_data()
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
    finally:
        conn.close()
