'''
Example for an "Xiaomi miflora sensor" with GPIO controlled Relay.
"TimerAgent" is for lighting and "TresholdAgent" for watering.
'''

import json
import os
import time as time
from abc import ABC, abstractmethod
from datetime import datetime

from ..backend import BackendAdapter
from ..sensor_data import SensorData
from .agents import Agent, create_agent_from_json
from .sensor import Sensor, create_sensor_from_json
from .math import argmin, average

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    '''Mock gpio calls on a non RPi machine'''
    from .mock_gpio import GPIO

DEFAULT_CONFIG_PATH = 'config.json'


class BaseDevice(ABC):
    def __init__(self, adapter: BackendAdapter):
        '''Eager init sensor credetials'''
        self.adapter = adapter
        self.sensors: list[Sensor] = []
        self.agents: list[Agent] = []
        self.id, self.key = self.read_auth_settings()

        self.log(f'Sensor with {self.id}:{self.key}')

        GPIO.setwarnings(False)
        GPIO.cleanup()
        time.sleep(0.1)
        GPIO.setmode(GPIO.BCM)
                
    def get_config(self):
        env_config = os.environ.get('CONFIG')
        if env_config is not None:
            return env_config
        return DEFAULT_CONFIG_PATH

    def get_creds(self) -> tuple[int, str]:
        return (self.id, self.key)

    def read_auth_settings(self) -> tuple[int, str]:
        with open(self.get_config(), 'r') as config_file:
            settings = json.load(config_file)['auth']
            return (settings['id'], settings['key'])

    def read_agent_settings(self) -> list:
        with open(self.get_config(), 'r') as config_file:
            return json.load(config_file)['agents']
    
    def read_sensor_settings(self) -> list:
        with open(self.get_config(), 'r') as config_file:
            return json.load(config_file)['sensors']

    def log(self, msg: str):
        print(f'\033[94mDevice [{datetime.utcnow().ctime()} UTC]\033[0m {msg}')
        

    @abstractmethod
    def on_agent_cmd(self, agent_index: int, cmd: int):
        raise NotImplementedError('on_agent_cmd not implemented')

    @abstractmethod
    def get_sensor_data(self) -> SensorData:
        raise NotImplementedError('get_sensor_data not implemented')

class Device(BaseDevice):
    def __init__(self, adapter: BackendAdapter):
        '''Setups miflora sensor and GPIOs'''
        super().__init__(adapter)
        
        for json_file in self.read_sensor_settings():
            sensor  = create_sensor_from_json(json_file)
            self.log(f'Added sensor: {sensor}')
            self.sensors.append(sensor)
        for json_file in self.read_agent_settings():
            agent = create_agent_from_json(json_file)
            self.log(f'Added agent: {agent}')
            self.agents.append(agent)
    
    def failsaife(self):
        '''Turn off all agents'''
        for agent in self.agents:
            agent.failsaife()

    def on_agent_cmd(self, index: int, cmd: int):
        '''Converts the recevived i64 into an actual command for the (alpabetically ordered) agent'''
        self.agents[index].set_state(cmd)

    def get_sensor_data(self) -> SensorData:
        '''Fetches and cummulates the sensor data'''
        data = []
        for sensor in self.sensors:
            sensor_data = sensor.get_sensor_data()
            if data is not None:
                data.append(sensor_data)

        def nomalize(data, key):
            values = list(map(lambda x: x.get(key), data))
            return list(filter(lambda x: x is not None, values))

        return SensorData(
            battery=argmin(nomalize(data, 'battery')),
            conductivity=average(nomalize(data, 'conductivity')),
            light=average(nomalize(data, 'light')),
            moisture=average(nomalize(data, 'moisture')),
            temperature=average(nomalize(data, 'temperature')),
        )
