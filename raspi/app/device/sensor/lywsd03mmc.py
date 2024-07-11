import lywsd03mmc

from typing import Optional
from app.backend import SensorData
from .base import Sensor


class Lywsd03mmcSensor(Sensor):

    def __init__(self, mac: str):
        super().__init__()
        self._mac = mac

    def get_sensor_data(self) -> Optional[SensorData]:
        client = lywsd03mmc.Lywsd03mmcClient(self._mac)
        data: lywsd03mmc.SensorDataBattery = client.data

        return SensorData(
            battery=data.battery,
            moisture=None,
            light=None,
            temperature=data.temperature,
            conductivity=None,
            humidity=data.humidity,
        )

    def __str__(self) -> str:
        return f"Lywsd03mmcSensor[{self._mac}]"
