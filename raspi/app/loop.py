import threading
import time as t
from datetime import datetime
import os

import paho.mqtt.client as mqtt

from .backend import BackendAdapter
from .device.device import Device
from .sensor_data import SensorData

# Constants
COMMAND_TOPIC = 'sensor/cmd'
DATA_TOPIC = 'sensor/data'
LOG_TOPIC = 'sensor/log'
DISCONNECT_TOPIC = 'ripe/master'


class MqttContext:
    def __init__(self, adapter: BackendAdapter, device: Device, sensor_id: int, sensor_key: str):
        super().__init__()
        self.adapter = adapter
        self.device = device
        self.id = sensor_id
        self.key = sensor_key
        self.client: mqtt.Client = None

    def connect(self):
        self.log("Connecting to control server")
        broker: str = None
        while broker is None:
            # done in a while, as backend may be temporary unavailable
            try:
                broker = self.adapter.fetch_sensor_broker(self.id, self.key)
            except Exception as e:
                t.sleep(0.5)

        self.log(f"Control server assigned broker {broker}")

        if broker.startswith('tcp://'):
            broker = broker[len('tcp://')::]
        (uri, portStr) = broker.split(':')

        if self.client is not None:
            self._clear_callbacks()
            self.client.loop_stop()
        self.client = mqtt.Client()

        # listen mqtt-commands and register callbackss
        self.client.on_connect = lambda _cli, _, __, ___: self._on_mqtt_connect()
        self.client.on_disconnect = lambda _cli, _, __: self._on_mqtt_disconnect()
        self.client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)

        self.client.connect(uri, int(portStr), keepalive=10)
        self.client.loop_start()
        self.log(f"Connected to {broker}")

        curr_client = self.client

        def timeout_fn():
            if not curr_client.is_connected():
                self.log("Client is not connected - retrying")
                self.connect()
        threading.Timer(10, timeout_fn).start()

    def publish(self, data: SensorData):
        self.client.publish(
            f'{DATA_TOPIC}/{self.id}/{self.key}', payload=data.json()
        )

    def log(self, msg: str):
        print(f'\033[92mMQTT [{datetime.utcnow().ctime()} UTC]\033[0m {msg}')
        try:
            self.client.publish(
                f'{LOG_TOPIC}/{self.id}/{self.key}', payload=msg)
        except:
            pass

    def _clear_callbacks(self):
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
        self.device.failsaife()
        self.connect()

    def _on_mqtt_message(self,  message: mqtt.MQTTMessage):
        topic: str = message.topic
        self.log(f"CMD: {topic} {message.payload}")
        if topic == DISCONNECT_TOPIC:
            self.log("Broker master disconnected - reconnecting on new broker")
            self.connect()
        else:
            for i in range(len(message.payload)):
                self.device.on_agent_cmd(i, message.payload[i])


def kickoff(base_url):
    adapter = BackendAdapter(base_url)
    device = Device(adapter)

    rollback_cmd = os.environ.get('RIPE_LOOP_ROLLBACK_CMD')
    if rollback_cmd:
        device.log(f'Rollback cmd {rollback_cmd}')
    else:
        device.log('No rollback cmd')

    sensor_id, sensor_key = device.get_creds()

    mqtt_context = MqttContext(adapter, device, sensor_id, sensor_key)
    mqtt_context.connect()

    while True:
        try:
            payload = device.get_sensor_data()
            mqtt_context.publish(payload)
            mqtt_context.log("published sensordata")
        except Exception as e:
            # Rollback logic
            if rollback_cmd is not None:
                rollback_succeeded = os.system(rollback_cmd) == 0
                mqtt_context.log(
                    f"Failed publishing due {e.__class__}, rollback succeeded: {rollback_succeeded}")
                if rollback_succeeded:
                    t.sleep(10)
                    continue
            else:
                mqtt_context.log(f"Failed publishing {e.__class__}")

        # timeout
        t.sleep(120)
