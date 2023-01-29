import time as t
import sys
import paho.mqtt.client as mqtt
from typing import Final

from app.util.log import logger
from .backend import BackendAdapter, SensorData
from .device import Device

# Constants
COMMAND_TOPIC = 'sensor/cmd'
DATA_TOPIC = 'sensor/data'
LOG_TOPIC = 'sensor/log'
DISCONNECT_TOPIC = 'ripe/master'


class MqttContext:
    def __init__(self, adapter: BackendAdapter, device: Device, sensor_id: int, sensor_key: str):
        super().__init__()
        self.adapter: Final[BackendAdapter] = adapter
        self.device: Final[Device] = device
        self.id: Final[int] = sensor_id
        self.key: Final[str] = sensor_key
        self.client: Final[mqtt.Client] = mqtt.Client()

    def connect(self, tries=10):
        self.log("Connecting to control server")
        broker: str = None
        while broker is None:
            try:
                broker = self.adapter.fetch_sensor_broker(self.id, self.key)
            except Exception as e:
                logger.error(f'Failed to connect to broker: {e}')
                tries -= 1
                if tries < 0:
                    logger.critical('Failed to reconnect, aborting')
                    sys.exit(-1)
                t.sleep(1)

        self.log(f"Control server assigned broker {broker}")

        if broker.startswith('tcp://'):
            broker = broker[len('tcp://')::]
        (uri, portStr) = broker.split(':')

        if self.client is not None:
            self._clear_callbacks()
            self.client.loop_stop()

        # listen mqtt-commands and register callbackss
        self.client.on_connect = lambda _cli, _, __, ___: self._on_mqtt_connect()
        self.client.on_disconnect = lambda _cli, _, __: self._on_mqtt_disconnect()
        self.client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)

        self.client.will_set(
            f'{LOG_TOPIC}/{self.id}/{self.key}', 'LOST_CONNECTION')
        self.client.connect(uri, int(portStr), keepalive=10, )
        self.client.loop_start()
        self.log(f"Connected to {broker}")

    def publish(self, data: SensorData):
        self.client.publish(
            f'{DATA_TOPIC}/{self.id}/{self.key}', payload=data.json()
        )

    def log(self, msg: str):
        logger.info(msg)
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
            self.device.failsaife()
            self.connect()
        else:
            for i in range(len(message.payload)):
                self.device.on_agent_cmd(i, message.payload[i])
