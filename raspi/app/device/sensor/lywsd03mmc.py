import lywsd03mmc

from typing import Optional
from app.backend import SensorData
from .base import Sensor

import lywsd03mmc


class Lywsd03mmcSensor(Sensor):

    def __init__(self, mac: str):
        super().__init__()
        self._mac = mac
        self._client = lywsd03mmc.Lywsd03mmcClient(self._mac)

    async def get_sensor_data(self) -> Optional[SensorData]:
        try:
            data: lywsd03mmc.SensorDataBattery = self._client.data  # implicit connect

            return SensorData(
                battery=data.battery,
                moisture=None,
                light=None,
                temperature=data.temperature,
                conductivity=None,
                humidity=data.humidity,
            )
        except Exception as e:
            print(f"Failed to get sensor data: {e}")
            return None

    def __str__(self) -> str:
        return f"Lywsd03mmcSensor[{self._mac}]"
