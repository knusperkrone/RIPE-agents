from abc import ABC, abstractmethod
from typing import Optional

from app.backend import SensorData


class Sensor(ABC):
    @abstractmethod
    async def get_sensor_data(self) -> Optional[SensorData]:
        raise NotImplementedError("register_backend not implemented")
