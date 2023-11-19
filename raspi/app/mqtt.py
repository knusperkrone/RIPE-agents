import time as t
import os
import paho.mqtt.client as mqtt
from typing import Final, Optional

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
        self,
        adapter: BackendAdapter,
        device: Device,
        sensor_id: int,
        sensor_key: str,
        version: str,
    ):
        super().__init__()
        self.adapter: Final[BackendAdapter] = adapter
        self.device: Final[Device] = device
        self.id: Final[int] = sensor_id
        self.key: Final[str] = sensor_key
        self.version: Final[str] = version
        self.client: Optional[mqtt.Client] = None
        self.is_connecting = False
        self.pepper = int(t.time())

    def connect(self, tries=10):
        if self.is_connecting:
            logger.warn("Device is already connecting")
            return

        self.is_connecting = True
        try:
            if self.client is not None:
                self.client.on_disconnect = None
                self.client.loop_stop()

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

            client_id = f"sensor-{self.version}-{self.id}-{self.pepper}"
            if broker.startswith("tcp://"):
                self.client = mqtt.Client(
                    client_id=client_id,
                    reconnect_on_failure=False,
                    protocol=mqtt.MQTTv5,
                )
                broker = broker[len("tcp://") : :]
                (uri, portStr) = broker.split(":")
            elif broker.startswith("wss://"):
                self.client = mqtt.Client(
                    transport="websockets",
                    client_id=client_id,
                    reconnect_on_failure=False,
                    protocol=mqtt.MQTTv5,
                )
                self.client.tls_set()
                broker = broker[len("wss://") : :]
                (uri, portStr) = broker.split(":")
            else:
                raise Exception(f"Unknown broker protocol: {broker}")

            self.client.on_connect = (
                lambda _cli, _, __, ___, ____,: self._on_mqtt_connect()
            )
            self.client.on_disconnect = lambda _cli, _, __: self._on_mqtt_disconnect()
            self.client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)
            self.client.connect(
                uri,
                int(portStr),
                keepalive=30,
            )
            self.client.loop_start()
            logger.info(f"Connected to {broker}")
        except Exception as e:
            logger.error(f"Failed to connect to broker: {e}")
            t.sleep(1.0)
            self.is_connecting = False
            self.connect(tries - 1)
        finally:
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

    def _on_mqtt_connect(self):
        # Notfy master about self disconnect
        self.client.will_set(
            f"{LOG_TOPIC}/{self.id}/{self.key}", payload="Lost connection", qos=2
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
