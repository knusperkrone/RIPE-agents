import json
import time as t
from datetime import datetime

import paho.mqtt.client as mqtt
import requests as r

from .device.device import Device
from .model import SensorData

# Constants
COMMAND_TOPIC = 'sensor/cmd'
DATA_TOPIC = 'sensor/data'
LOG_TOPIC = 'sensor/log'
DISCONNECT_TOPIC = 'ripe/master'
# BASE_URL = 'http://192.168.178.22:8000/api'
BASE_URL = 'http://ripe.feste-ip.net:35962/api'


class MqttContext:
    def __init__(self, sensor_id: int, sensor_key: str):
        super().__init__()
        self.id = sensor_id
        self.key = sensor_key

    def connect(self):
        print(f"[{datetime.now().ctime()}] Connecting .", end='', flush=True)
        broker: str = None
        while broker is None:
            # done in a while, as backend may be temporary unavailable
            try:
                print('.', end='', flush=True)
                broker = self._fetch_sensor_broker()
            except Exception:
                t.sleep(0.5)
        print(f"[{datetime.now().ctime()}] Assigned broker {broker}")

        if broker.startswith('tcp://'):
            broker = broker[len('tcp://')::]
        parts = broker.split(':')
        self.client: mqtt.Client = mqtt.Client()
        self.client.connect(parts[0], int(parts[1]))

        # listen mqtt-commands and register callbackss
        self.client.on_connect = on_mqtt_connect
        self.client.on_disconnect = on_mqtt_disconnect
        self.client.on_message = on_mqtt_message
        self.client.subscribe(f'{COMMAND_TOPIC}/{self.id}/{self.key}')
        self.client.subscribe(f'{DISCONNECT_TOPIC}')
        self.client.loop_start()

    def publish(self, data: SensorData):
        self.client.publish(
            f'{DATA_TOPIC}/{self.id}/{self.key}', payload=data.json()
        )

    def log(self, msg: str):
        print(f'[{datetime.now().ctime()}] {msg}')
        self.client.publish(f'{LOG_TOPIC}/{self.id}/{self.key}', payload=msg)

    def clear_callbacks(self):
        self.client.on_connect = None
        self.client.on_disconnect = None
        self.client.on_message = None

    def _fetch_sensor_broker(self):
        return r.get(f'{BASE_URL}/sensor/{self.id}/{self.key}').json()['broker']


def on_mqtt_connect(client: mqtt.Client, userdata, flags, rc):
    mqtt_context.log(f"Mqtt connected")


def on_mqtt_disconnect(client: mqtt.Client, userdata, rc):
    mqtt_context.log(f"Mqtt disconnected - reconnecting")
    mqtt_context.connect()


def on_mqtt_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    topic: str = message.topic
    mqtt_context.log(f"CMD: {topic} {message.payload}")
    if topic == DISCONNECT_TOPIC:
        print("Broker master disconnected - reconnecting on new broker")
        mqtt_context.clear_callbacks()
        mqtt_context.connect()
    else:
        for i in range(len(message.payload)):
            custom_device.on_agent_cmd(i, message.payload[i])


# global objects
custom_device: Device = None
mqtt_context: MqttContext = None


def kickoff():
    global custom_device, mqtt_context

    custom_device = Device()
    sensor_id, sensor_key = custom_device.get_creds()
    print(f"[Sensor {sensor_id}]")

    mqtt_context = MqttContext(sensor_id, sensor_key)
    mqtt_context.connect()

    while True:
        try:
            payload = custom_device.get_sensor_data()
            mqtt_context.log("published sensordata")
            mqtt_context.publish(payload)
        except Exception as e:
            mqtt_context.log(f"Failed publishing {e.__class__}")

        # timeout
        t.sleep(60)
