from typing import Optional
from bleak import BleakClient
from dataclasses import dataclass
import struct


from app.backend import SensorData
from app.util.log import logger
from .base import Sensor


@dataclass
class Lywsd03mmcData:
    temperature: float
    humidity: float
    battery: int


class Lywsd03mmcClient:
    HUMIDITY_UUID = "00002a6f-0000-1000-8000-00805f9b34fb"
    TEMPERATURE_UUID = "00002a1f-0000-1000-8000-00805f9b34fb"
    BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

    def __init__(self, mac_or_uuid: str, timeout: float):
        self.mac_or_uuid = mac_or_uuid
        self.client = BleakClient(
            address_or_ble_device=self.mac_or_uuid, timeout=timeout
        )

    def is_connected(self):
        return self.client.is_connected

    async def connect(self) -> bool:
        return await self.client.connect()

    async def get_data(self) -> Lywsd03mmcData:
        res: bytearray = await self.__get_attribute(self.TEMPERATURE_UUID)
        (temp_int,) = struct.unpack_from("<h", res)
        res: bytearray = await self.__get_attribute(self.HUMIDITY_UUID)
        (hum_int,) = struct.unpack_from("<h", res)
        battery_int = await self.__get_attribute(self.BATTERY_UUID)
        battery = int.from_bytes(battery_int, byteorder="little")
        return Lywsd03mmcData(
            temperature=temp_int / 10, humidity=hum_int / 100, battery=battery
        )

    async def __get_attribute(self, attribute_name: str):
        return await self.client.read_gatt_char(attribute_name)

    async def close(self):
        if self.client.is_connected:
            await self.client.disconnect()


class Lywsd03mmcSensor(Sensor):

    def __init__(self, mac: str):
        super().__init__()
        self._mac = mac
        self._client = Lywsd03mmcClient(self._mac, timeout=20.0)

    async def get_sensor_data(self) -> Optional[SensorData]:
        try:
            if not self._client.is_connected():
                await self._client.connect()

            data: Lywsd03mmcData = await self._client.get_data()
            return SensorData(
                battery=data.battery,
                moisture=None,
                light=None,
                temperature=data.temperature,
                conductivity=None,
                humidity=data.humidity,
            )
        except Exception as e:
            logger.error(f"Failed to get sensor data: {e}")
            return None
