import paho.mqtt.client as mqtt
import json
from pets.tasks import process_biometric_data

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT")
    client.subscribe("pet/biometric/#")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        pet_id = topic.split('/')[-1]
        process_biometric_data.delay(pet_id, payload)
    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()