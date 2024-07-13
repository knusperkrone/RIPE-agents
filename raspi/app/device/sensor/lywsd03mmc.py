import lywsd03mmc

from typing import Optional

from app.backend import SensorData
from app.util.log import logger
from .base import Sensor


class Lywsd03mmcSensor(Sensor):

    def __init__(self, mac: str):
        super().__init__()
        self._mac = mac
        self._client = lywsd03mmc.Lywsd03mmcClient(self._mac)
        self._last_data: Optional[lywsd03mmc.SensorDataBattery] = None

    async def get_sensor_data(self) -> Optional[SensorData]:
        try:
            data: lywsd03mmc.SensorDataBattery = self._client.data  # implicit connect
            self._last_data = data

            return self._transform_data(data)
        except Exception as e:
            logger.error(f"Failed to get sensor data: {e}")
            if self._last_data:
                return self._transform_data(self._last_data)
            return None

    def _transform_data(self, data: lywsd03mmc.SensorDataBattery) -> SensorData:
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
