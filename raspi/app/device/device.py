from app.util.math import argmin, average
from app.util.log import logger
from app.backend import BackendAdapter, SensorData

from .base import BaseDevice
from .agent import create_agent_from_json
from .sensor import create_sensor_from_json


class Device(BaseDevice):
    def __init__(self, adapter: BackendAdapter):
        """Setups miflora sensor and GPIOs"""
        super().__init__(adapter)

        for json_file in self.read_sensor_settings():
            sensor = create_sensor_from_json(json_file)
            self.sensors.append(sensor)
            logger.info(f"Added sensor: {sensor}")
        for json_file in self.read_agent_settings():
            agent = create_agent_from_json(json_file)
            self.agents.append(agent)
            logger.info(f"Added agent: {agent}")

    def failsaife(self):
        """Turn off all agents"""
        logger.warn("Setting device in Failsafe state")
        for agent in self.agents:
            agent.failsaife()

    def on_agent_cmd(self, index: int, cmd: int):
        """Converts the recevived i64 into an actual command for the (alpabetically ordered) agent"""
        self.agents[index].set_state(cmd)

    def get_sensor_data(self) -> SensorData:
        """Fetches and cummulates the sensor data"""
        data = []
        for sensor in self.sensors:
            sensor_data = sensor.get_sensor_data()
            if data is not None:
                data.append(sensor_data)

        def filter(data, key):
            values = list(map(lambda x: x.get(key), data))
            return list(filter(lambda x: x is not None, values))

        return SensorData(
            battery=argmin(filter(data, "battery")),
            conductivity=average(filter(data, "conductivity")),
            light=average(filter(data, "light")),
            moisture=average(filter(data, "moisture")),
            temperature=average(filter(data, "temperature")),
            humidity=average(filter(data, "humidity")),
        )
