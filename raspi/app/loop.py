import json
import time as t
import traceback
from datetime import datetime

import paho.mqtt.client as mqtt
import requests as r

from .backend import BackendAdapter
from .device.device import Device
from .model import SensorData

# Constants
COMMAND_TOPIC = 'sensor/cmd'
DATA_TOPIC = 'sensor/data'
LOG_TOPIC = 'sensor/log'
DISCONNECT_TOPIC = 'ripe/master'

DEFAULT_URL = 'http://localhost:8080/api'


class MqttContext:
    def __init__(self, adapter: BackendAdapter, device: Device, sensor_id: int, sensor_key: str):
        super().__init__()
        self.adapter = adapter
        self.device = device
        self.id = sensor_id
        self.key = sensor_key

    def connect(self):
        print(f"[{datetime.utcnow().ctime()} UTC] Connecting .",
              end='', flush=True)
        broker: str = None
        while broker is None:
            # done in a while, as backend may be temporary unavailable
            try:
                print('.', end='', flush=True)
                broker = self.adapter.fetch_sensor_broker(self.id, self.key)
            except Exception as e:
                t.sleep(0.5)
        print(f"[{datetime.utcnow().ctime()} UTC] Assigned broker {broker}")

        if broker.startswith('tcp://'):
            broker = broker[len('tcp://')::]
        parts = broker.split(':')  
              
        if self.client is not None:
            self.client.loop_stop()
        self.client: mqtt.Client = mqtt.Client()
        self.client.connect(parts[0], int(parts[1]))

        # listen mqtt-commands and register callbackss
        self.client.on_connect = lambda _cli, _, __, ___: self._on_mqtt_connect()
        self.client.on_disconnect = lambda _cli, _, __, ___: self._on_mqtt_disconnect()
        self.client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)
        self.client.loop_start()

    def publish(self, data: SensorData):
        self.client.publish(
            f'{DATA_TOPIC}/{self.id}/{self.key}', payload=data.json()
        )

    def log(self, msg: str):
        print(f'[{datetime.utcnow().ctime()} UTC] {msg}')
        self.client.publish(f'{LOG_TOPIC}/{self.id}/{self.key}', payload=msg)

    def clear_callbacks(self):
        self.client.on_connect = None
        self.client.on_disconnect = None
        self.client.on_message = None

    def _on_mqtt_connect(self):
        # Notfy master about self disconnect
        self.client.will_set(
            f'{LOG_TOPIC}/{self.id}/{self.key}',
            payload='Lost connection'
        )
        # Get notified about master disconnect
        self.client.subscribe(f'{DISCONNECT_TOPIC}')
        # listen commands
        self.client.subscribe(f'{COMMAND_TOPIC}/{self.id}/{self.key}')

        self.log(f"Mqtt connected")

    def _on_mqtt_disconnect(self):
        self.log(f"Mqtt disconnected - reconnecting")
        self.connect()

    def on_mqtt_message(self,  message: mqtt.MQTTMessage):
        topic: str = message.topic
        self.log(f"CMD: {topic} {message.payload}")
        if topic == DISCONNECT_TOPIC:
            self.log("Broker master disconnected - reconnecting on new broker")
            self.clear_callbacks()
            self.connect()
        else:
            for i in range(len(message.payload)):
                self.device.on_agent_cmd(i, message.payload[i])


def kickoff(base_url: str = DEFAULT_URL):
    adapter = BackendAdapter(base_url)
    device = Device(adapter)

    sensor_id, sensor_key = device.get_creds()
    print(f"[Sensor {sensor_id} with {base_url}]")

    mqtt_context = MqttContext(adapter, device, sensor_id, sensor_key)
    mqtt_context.connect()

    while True:
        try:
            payload = device.get_sensor_data()
            mqtt_context.publish(payload)
            mqtt_context.log("published sensordata")
        except Exception as e:
            mqtt_context.log(f"Failed publishing {e.__class__}")
            traceback.print_tb(e.__traceback__)

        # timeout
        t.sleep(120)
