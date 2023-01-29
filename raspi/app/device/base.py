'''
Example for an "Xiaomi miflora sensor" with GPIO controlled Relay.
"TimerAgent" is for lighting and "TresholdAgent" for watering.
'''

import json
import os
import time as time
from abc import ABC, abstractmethod
from typing import Final

from app.util.log import logger
from app.backend import BackendAdapter, SensorData
from .agent import Agent
from .sensor import Sensor

DEFAULT_CONFIG_PATH = 'config.json'


class BaseDevice(ABC):
    def __init__(self, adapter: BackendAdapter):
        '''Eager init sensor credetials'''
        self.adapter: Final[BackendAdapter] = adapter
        self.sensors: Final[list[Sensor]] = []
        self.agents: Final[list[Agent]] = []
        self.id, self.key = self.read_auth_settings()

        logger.info(f'Starting Device[{self.id}:{self.key}]')

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
            if settings.get('id') is None:
                raise EnvironmentError(f'No auth.id in {self.get_config()}')
            if settings.get('key') is None:
                raise EnvironmentError(f'No auth.key in {self.get_config()}')
            return (settings['id'], settings['key'])

    def read_agent_settings(self) -> list:
        with open(self.get_config(), 'r') as config_file:
            return json.load(config_file)['agents']

    def read_sensor_settings(self) -> list:
        with open(self.get_config(), 'r') as config_file:
            return json.load(config_file)['sensors']

    @abstractmethod
    def on_agent_cmd(self, agent_index: int, cmd: int):
        raise NotImplementedError('on_agent_cmd not implemented')

    @abstractmethod
    def get_sensor_data(self) -> SensorData:
        raise NotImplementedError('get_sensor_data not implemented')
