import time as t
import os
import paho.mqtt.client as mqtt
from typing import Final, Optional

from app.util.log import logger
from .backend import BackendAdapter, Broker, SensorData
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

    def connect_or_die(self, tries=10):
        if self.is_connecting:
            logger.warn("Device is already connecting")
            return
        elif tries <= 0:
            logger.critical("Failed to (re-)connect, exiting")
            os._exit(8)

        client_id = f"sensor-{self.version}-{self.id}-{self.pepper}"
        self.is_connecting = True

        try:
            # Cleanup old client
            if self.client is not None:
                self.client.on_disconnect = None
                self.client.loop_stop()
                self.client.disconnect()

            # Get available brokers from master
            logger.info("Contacting master server")
            brokers = self._get_brokers_from_master_or_die()
            logger.info(
                f"Control server returned brokers {list(map(lambda x: str(x), brokers))}"
            )

            # First fit connection
            for broker in brokers:
                try:
                    logger.info(f"Try connecting to {broker}")
                    self.client = self._connect_to_broker_blocking(broker, client_id)
                    break
                except Exception as e:
                    logger.warn(f"Failed to connect to {broker} - {e}")

            if self.client is None:
                raise Exception("No broker could be contacted")
            self.client.loop_start()
            self.log(f"Connected to {broker}")

        except Exception as e:
            logger.error(f"Connect failed, {tries} tries left: {e}")
            t.sleep(5.0)
            self.is_connecting = False
            self.connect_or_die(tries - 1)
        finally:
            self.is_connecting = False

    def is_connected(self) -> bool:
        assert self.client is not None
        return self.client.is_connected()

    def publish(self, data: SensorData):
        self._publish(f"{DATA_TOPIC}/{self.id}/{self.key}", data.json())

    def log(self, msg: str):
        logger.info(f"[MQTT_LOG] {msg}")
        self._publish(f"{LOG_TOPIC}/{self.id}/{self.key}", msg)

    def _get_brokers_from_master_or_die(self, tries=10) -> list[Broker]:
        while tries >= 0:
            try:
                return self.adapter.fetch_sensor_brokers(self.id, self.key)
            except Exception as e:
                logger.error(
                    f"Failed to connect master server, {tries} retries left: {e}"
                )
                tries -= 1
            t.sleep(1)

        logger.critical("Failed to retrieve - exiting")
        os._exit(8)

    def _connect_to_broker_blocking(
        self, broker: Broker, client_id: str
    ) -> mqtt.Client:
        client = self._build_mqtt_client(broker, client_id)

        connecting_status = "waiting"

        def on_connect(rc: int):
            nonlocal self, connecting_status
            if rc == mqtt.MQTT_ERR_SUCCESS:
                connecting_status = "success"
                client.subscribe(f"{DISCONNECT_TOPIC}", qos=2)
                client.subscribe(f"{COMMAND_TOPIC}/{self.id}/{self.key}", qos=2)

        def on_disconnect(rc):
            nonlocal self, connecting_status
            if connecting_status == "waiting":
                connecting_status = mqtt.error_string(rc)
            else:
                self._failsaife_and_reconnect()

        client.on_connect = lambda _cli, _userdata, _, rc, __,: on_connect(rc)
        client.on_disconnect = lambda _cli, _userdata, rc, _props: on_disconnect(rc)
        client.on_message = lambda _, __, msg: self._on_mqtt_message(msg)
        client.will_set(
            f"{LOG_TOPIC}/{self.id}/{self.key}", payload="Lost connection", qos=2
        )

        client.connect(
            broker.host,
            broker.port,
            keepalive=30,
        )

        while connecting_status == "waiting":
            client.loop()
            t.sleep(0.1)

        if connecting_status != "success":
            raise Exception(f"{connecting_status}")

        return client

    def _build_mqtt_client(self, broker: Broker, client_id: str) -> mqtt.Client:
        client = None
        if broker.scheme == "tcp":
            client = mqtt.Client(
                client_id=client_id,
                reconnect_on_failure=False,
                protocol=mqtt.MQTTv5,
            )
        elif broker.scheme == "wss":
            client = mqtt.Client(
                transport="websockets",
                client_id=client_id,
                reconnect_on_failure=False,
                protocol=mqtt.MQTTv5,
            )
            client.tls_set()
        else:
            raise Exception(f"Unsupported broker protocol: {broker}")

        if broker.credentials is not None:
            client.username_pw_set(
                username=broker.credentials.username,
                password=broker.credentials.password,
            )

        return client

    def _publish(self, topic, payload):
        try:
            self.client.publish(topic, payload=payload, qos=2)
        except Exception as e:
            logger.warn(f"Failed to publish to MQTT: {e}")

    def _failsaife_and_reconnect(self):
        logger.error(f"Mqtt disconnected - reconnecting")
        self.device.failsaife()
        self.is_connecting = False
        self.connect_or_die()

    def _on_mqtt_message(self, message: mqtt.MQTTMessage):
        topic: str = message.topic
        self.log(f"CMD: {topic} {message.payload}")
        if topic == DISCONNECT_TOPIC:
            self.log("Master disconnected - reconnecting on new broker")
            self.device.failsaife()
            self.connect_or_die()
        else:
            for i in range(len(message.payload)):
                self.device.on_agent_cmd(i, message.payload[i])
