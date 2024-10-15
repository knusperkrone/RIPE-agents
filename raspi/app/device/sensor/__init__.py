from .base import Sensor
#from .miflora import MiFloraSensor
#from .lywsd03mmc import Lywsd03mmcSensor


def create_sensor_from_json(json) -> Sensor:
    type = json["type"]
#    if type == "miflora":
#        return MiFloraSensor(json["mac"])
#    elif type == "lywsd03mmc":
#        return Lywsd03mmcSensor(json["mac"])
#    else:
    raise NotImplementedError(f"Invalid agent-type: {type}")
