import asyncio
from typing import cast, Union, Optional

from app.util.math import average, argmin
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
        """Converts the received i64 into an actual command for the (alphabetically ordered) agent"""
        try:
            self.agents[index].set_state(cmd)
        except IndexError:
            logger.error(f"Index {index} out of range")
        except Exception as e:
            logger.error(f"Error setting {self.agents[index]} state: {e}")

    async def get_sensor_data(self) -> SensorData:
        """Fetches and cumulates the sensor data"""
        data_list: list[SensorData] = []
        for sensor in self.sensors:
            try:
                sensor_data = await asyncio.wait_for(
                    sensor.get_sensor_data(), timeout=20.0
                )
                if sensor_data is not None:
                    data_list.append(sensor_data)
            except Exception as e:
                logger.error(f"Error fetching {sensor} data: {e}")

        def normalize(data_list: list[SensorData], key: str) -> list[Union[int, float]]:
            values = map(lambda x: x.get(key), data_list)
            return list(filter(lambda x: x is not None, values))

        return SensorData(
            battery=cast(Optional[int], argmin(normalize(data_list, "battery"))),
            conductivity=cast(
                Optional[int], average(normalize(data_list, "conductivity"))
            ),
            light=cast(Optional[int], average(normalize(data_list, "light"))),
            moisture=cast(Optional[float], average(normalize(data_list, "moisture"))),
            temperature=cast(
                Optional[float], average(normalize(data_list, "temperature"))
            ),
            humidity=cast(Optional[float], average(normalize(data_list, "humidity"))),
        )
