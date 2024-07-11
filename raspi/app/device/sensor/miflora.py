from btlewrap.bluepy import BluepyBackend
from miflora import miflora_poller

from app.backend import SensorData
from .base import Sensor


class MiFloraSensor(Sensor):
    def __init__(self, mac: str):
        super().__init__()
        self.mac = mac
        self.poller = miflora_poller.MiFloraPoller(mac, BluepyBackend)

    def get_sensor_data(self) -> SensorData:
        try:
            self.poller.clear_cache()
            self.poller.fill_cache()

            return SensorData(
                battery=int(self.poller.battery),
                moisture=float(self.poller.parameter_value(miflora_poller.MI_MOISTURE)),
                light=int(self.poller.parameter_value(miflora_poller.MI_LIGHT)),
                temperature=float(
                    self.poller.parameter_value(miflora_poller.MI_TEMPERATURE)
                ),
                conductivity=int(
                    self.poller.parameter_value(miflora_poller.MI_CONDUCTIVITY)
                ),
                humidity=None,
            )
        except Exception as e:
            print(f"Failed to get sensor data: {e}")
            return None

    def __str__(self) -> str:
        return f"MiFloraSensor[{self.mac}]"
