import time as t
import os
import paho.mqtt.client as mqtt
from typing import Final

from app.util.log import logger
from .backend import BackendAdapter, SensorData
from .device import Device

# Constants
COMMAND_TOPIC = "sensor/cmd"
DATA_TOPIC = "sensor/data"
LOG_TOPIC = "sensor/log"
DISCONNECT_TOPIC = "ripe/master"


class MqttContext:
    def __init__(
        self, adapter: BackendAdapter, device: Device, sensor_id: int, sensor_key: str
    ):
        super().__init__()
        self.adapter: Final[BackendAdapter] = adapter
        self.device: Final[Device] = device
        self.id: Final[int] = sensor_id
        self.key: Final[str] = sensor_key
        self.client: Final[mqtt.Client] = mqtt.Client(transport="websockets")
        self.is_connecting = False

    def connect(self, tries=10):
        if self.is_connecting:
            logger.warn("Device is already connecting")
            return

        self.is_connecting = True
        logger.info("Connecting to control server")

        broker: str = None
        while broker is None:
            try:
                broker = self.adapter.fetch_sensor_broker(self.id, self.key)
            except Exception as e:
                logger.error(f"Failed to connect to broker: {e}")
                tries -= 1
                if tries < 0:
                    logger.critical("Failed to reconnect, exiting programm")
                    os._exit(8)
                t.sleep(1)

        self.log(f"Control server assigned broker {broker}")

        if broker.startswith("tcp://"):
            self.client = mqtt.Client()
            broker = broker[len("tcp://") : :]
            (uri, portStr) = broker.split(":")
        elif broker.startswith("wss://"):
            self.client = mqtt.Client(transport="websockets")
            self.client.tls_set()
            broker = broker[len("wss://") : :]
            (uri, portStr) = broker.split(":")
        
            

        if self.client is not None:
            self._clear_callbacks()
            self.client.loop_stop()

        # listen mqtt-commands and register callbackss
        self.client.on_connect = lambda _cli, _, __, ___: self._on_mqtt_connect()
        self.client.on_disconnect = lambda _cli, _, __: self._on_mqtt_disconnect()
        self.client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)

        self.client.connect(
            uri,
            int(portStr),
            keepalive=30,
        )
        self.client.loop_start()
        logger.info(f"Connecting to {broker}")
        self.is_connecting = False

    def is_connected(self) -> bool:
        return self.client.is_connected()

    def publish(self, data: SensorData):
        self._publish(f"{DATA_TOPIC}/{self.id}/{self.key}", data.json())

    def log(self, msg: str):
        logger.info(msg)
        self._publish(f"{LOG_TOPIC}/{self.id}/{self.key}", msg)

    def _publish(self, topic, payload):
        try:
            self.client.publish(topic, payload=payload, qos=2)
        except Exception as e:
            logger.error(f"Failed to publish to MQTT: {e}")

    def _clear_callbacks(self):
        self.client.on_connect = None
        self.client.on_disconnect = None
        self.client.on_message = None

    def _on_mqtt_connect(self):
        # Notfy master about self disconnect
        self.client.will_set(
            f"{LOG_TOPIC}/{self.id}/{self.key}", payload="Lost connection"
        )
        # Get notified about master disconnect
        self.client.subscribe(f"{DISCONNECT_TOPIC}", qos=2)
        # Receive commands
        self.client.subscribe(f"{COMMAND_TOPIC}/{self.id}/{self.key}", qos=2)

        self.log(f"Mqtt connection etablished")

    def _on_mqtt_disconnect(self):
        self.log(f"Mqtt disconnected - reconnecting")
        self.device.failsaife()
        self.is_connecting = False
        self.connect()

    def _on_mqtt_message(self, message: mqtt.MQTTMessage):
        topic: str = message.topic
        self.log(f"CMD: {topic} {message.payload}")
        if topic == DISCONNECT_TOPIC:
            self.log("Broker master disconnected - reconnecting on new broker")
            self.device.failsaife()
            self.connect()
        else:
            for i in range(len(message.payload)):
                self.device.on_agent_cmd(i, message.payload[i])
