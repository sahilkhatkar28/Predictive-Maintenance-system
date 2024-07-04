const mqtt = require('mqtt');

// Replace with your MQTT broker address
const brokerUrl = 'mqtt://broker.hivemq.com:1883'; 

const options = {
  clientId: 'mqttjs01',
  username: 'yourUsername', // if applicable
  password: 'yourPassword', // if applicable
};

const client = mqtt.connect(brokerUrl, options);

client.on('connect', () => {
  console.log('Connected to MQTT broker');

  // Subscribe to topics
  client.subscribe('sensor/iot/temperature', (err) => {
    if (!err) {
      console.log('Subscribed to temperature topic');
    }
  });

  client.subscribe('sensor/iot/humidity', (err) => {
    if (!err) {
      console.log('Subscribed to humidity topic');
    }
  });
});

client.on('message', (topic, message) => {
  // message is a Buffer, convert to string
  const msg = message.toString();

  if (topic === 'sensor/iot/temperature') {
    console.log(`Temperature: ${msg} °C`);
  }

  if (topic === 'sensor/iot/humidity') {
    console.log(`Humidity: ${msg} %`);
  }
});

client.on('error', (error) => {
  console.error(`Connection error: ${error}`);
  client.end();
});
