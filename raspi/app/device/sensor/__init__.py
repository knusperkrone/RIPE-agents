from .base import Sensor
from .miflora import MiFloraSensor


def create_sensor_from_json(json) -> Sensor:
    type = json['type']
    if type == 'miflora':
        return MiFloraSensor(
            json['mac']
        )
    else:
        raise NotImplementedError(f'Invalid agent-type: {type}')
