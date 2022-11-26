from btlewrap.bluepy import BluepyBackend
from miflora import miflora_poller

from abc import ABC, abstractmethod

from app.sensor_data import SensorData

class Sensor(ABC):
    @abstractmethod
    def get_sensor_data(self) -> SensorData or None:
        raise NotImplementedError('register_backend not implemented')

class MiFloraSensor(Sensor):
    def __init__(self, mac: str):
        super().__init__()
        self.mac = mac
        self.poller = miflora_poller.MiFloraPoller(mac, BluepyBackend)

    def get_sensor_data(self) -> SensorData:
        self.poller.clear_cache()
        self.poller.fill_cache()

        return SensorData(
            battery=self.poller.battery,
            moisture=self.poller.parameter_value(
                miflora_poller.MI_MOISTURE),
            light=self.poller.parameter_value(miflora_poller.MI_LIGHT),
            temperature=self.poller.parameter_value(
                miflora_poller.MI_TEMPERATURE),
            conductivity=self.poller.parameter_value(
                miflora_poller.MI_CONDUCTIVITY)
        )

    def __str__(self) -> str:
        return f'MiFloraSensor[{self.mac}]'


def create_sensor_from_json(json) -> Sensor:
    type = json['type']
    if type == 'miflora':
        return MiFloraSensor(
            json['mac']
        )
    else:
        raise NotImplementedError(f'Invalid agent-type: {type}')
