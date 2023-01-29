from abc import ABC, abstractmethod

from app.backend import SensorData


class Sensor(ABC):
    @abstractmethod
    def get_sensor_data(self) -> SensorData or None:
        raise NotImplementedError('register_backend not implemented')
