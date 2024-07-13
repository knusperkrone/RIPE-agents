import time as t
import os
import aiomqtt
import asyncio
from typing import Final, Optional, cast

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
        self.client: Optional[aiomqtt.Client] = None

    async def kickoff(self, tries=10):
        client_id = f"sensor-{self.version}-{self.id}-{int(t.time())}"

        while True:
            self.client = None
            brokers = await self._get_brokers_from_master_or_die()
            for broker in brokers:
                try:
                    client = aiomqtt.Client(
                        broker.host,
                        broker.port,
                        transport=broker.scheme,
                        identifier=client_id,
                        username=broker.credentials.username,
                        password=broker.credentials.password,
                    )
                    async with client:
                        break
                except Exception as e:
                    logger.warn(f"Failed to connect to {broker} - {e}")
                    client = None
                    continue

            if client is None:
                logger.error(f"Failed connection to {broker}")
                asyncio.sleep(5.0)
                continue

            try:
                async with client:
                    self.client = client
                    await client.subscribe(f"{DISCONNECT_TOPIC}", qos=2)
                    await client.subscribe(
                        f"{COMMAND_TOPIC}/{self.id}/{self.key}", qos=2
                    )

                    async for message in client.messages:
                        try:
                            await self._on_mqtt_message(message)
                        except Exception as e:
                            await self.log(f"Failed to process message: {e}")
            except Exception as e:
                self.client = None
                self.device.failsaife()
                asyncio.sleep(2.0)

    def is_connected(self) -> bool:
        return self.client is not None

    async def publish(self, data: SensorData):
        await self._publish(f"{DATA_TOPIC}/{self.id}/{self.key}", data.json())

    async def log(self, msg: str):
        logger.info(f"[MQTT_LOG] {msg}")
        await self._publish(f"{LOG_TOPIC}/{self.id}/{self.key}", msg)

    async def _get_brokers_from_master_or_die(self, tries=10) -> list[Broker]:
        while tries >= 0:
            try:
                return await self.adapter.fetch_sensor_brokers(self.id, self.key)
            except Exception as e:
                logger.error(
                    f"Failed to connect master server, {tries} retries left: {e}"
                )
                tries -= 1
            t.sleep(1)

        logger.critical("Failed to retrieve - exiting")
        os._exit(8)

    async def _publish(self, topic, payload):
        try:
            await self.client.publish(topic, payload=payload, qos=2)
        except Exception as e:
            logger.warn(f"Failed to publish to MQTT: {e}")

    async def _on_mqtt_message(self, message: aiomqtt.Message):
        topic = cast(str, message.topic)
        payload = cast(bytearray, message.payload)
        await self.log(f"CMD: {topic} {payload}")
        if topic == DISCONNECT_TOPIC:
            await self.log("Master disconnected - reconnecting on new broker")
            self.device.failsaife()
            # TODO: Reconnect
        else:
            for i in range(len(cast(bytes, payload))):
                self.device.on_agent_cmd(i, payload[i])
