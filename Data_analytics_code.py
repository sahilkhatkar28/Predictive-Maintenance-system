import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db')

# Load data from SQLite into a Pandas DataFrame
df = pd.read_sql_query("SELECT * FROM SensorData", conn)

# Close the database connection
conn.close()

# Display the first few rows of the dataframe
print("Sample data:")
print(df.head())

# Data preprocessing
X = df[['temperature', 'vibration']].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)

# Isolation Forest model for anomaly detection
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

# Predict anomalies
df['anomaly'] = model.predict(X_scaled)
df['anomaly'] = df['anomaly'].map({1: 0, -1: 1})  # Convert predictions to binary: 0 (normal) or 1 (anomaly)

# Plotting anomalies
plt.figure(figsize=(12, 6))
plt.scatter(df.index, df['temperature'], c=df['anomaly'], cmap='coolwarm', s=20)
plt.title('Anomaly Detection: Temperature')
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.colorbar(label='Anomaly')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Classification report
print("\nClassification Report:")
print(classification_report(df['anomaly'], df['anomaly']))
