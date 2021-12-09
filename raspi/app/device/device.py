'''
Example for an "Xiaomi miflora sensor" with GPIO controlled Relay.
"TimerAgent" is for lighting and "TresholdAgent" for watering.
'''

import json
import time as time
from abc import ABC, abstractmethod
from typing import Tuple

from btlewrap.bluepy import BluepyBackend
from miflora import miflora_poller

from ..backend import BackendAdapter
from ..model import SensorData
from .relay import PWMDevice, RelayDevice

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    '''Mock gpio calls on a non RPi machine'''
    from .mock_gpio import GPIO


MIFLORA_MAC = 'C4:7C:8D:6B:C3:48'


class BaseDevice(ABC):
    def __init__(self, adapter: BackendAdapter):
        '''Eager init sensor credetials'''
        self.adapter = adapter
        self.register_sensor()

    def register_sensor(self):
        '''Uses persistet credentials, or registers a new sensor from the backend'''
        config_path = 'config.json'
        try:
            with open(config_path, 'r') as config_file:
                settings = json.load(config_file)
                self.id = settings['id']
                self.key = settings['key']
        except Exception:
            sensor_id, sensor_key = self.register_backend()
            with open(config_path, 'w') as config_file:
                json.dump({'id': sensor_id, 'key': sensor_key}, config_file)
            self.id = sensor_id
            self.key = sensor_key

    def get_creds(self) -> Tuple[int, str]:
        return (self.id, self.key)

    @abstractmethod
    def register_backend(self):
        raise Exception('register_backend not implemented')

    @abstractmethod
    def on_agent_cmd(self, agent_index: int, cmd: int):
        raise Exception('on_agent_cmd not implemented')

    @abstractmethod
    def get_sensor_data(self) -> SensorData:
        raise Exception('get_sensor_data not implemented')


class Device(BaseDevice):
    def __init__(self, adapter: BackendAdapter):
        '''Setups miflora sensor and GPIOs'''
        super().__init__(adapter)
        # Init xiamio sensor
        self.poller = miflora_poller.MiFloraPoller(MIFLORA_MAC, BluepyBackend)

        # Init GPIOs for relay control
        GPIO.cleanup()
        time.sleep(0.1)
        GPIO.setmode(GPIO.BCM)

        with open('gpios.json') as gpio_file:
            gpios = json.load(gpio_file)
            water_gpio = gpios['water']
            light_gpio = gpios['light']
            (pwm_wg, pwm_cp) = tuple(gpios['pwm'])

        self.light_relay = RelayDevice(water_gpio)
        self.water_relay = RelayDevice(light_gpio)
        self.pwm_device = PWMDevice(pwm_wg, pwm_cp)

    def register_backend(self) -> Tuple[int, str]:
        '''Actual backend calls to register the sensor and the specific agents (ordered alpabetically)'''
        (sensor_id, sensor_key) = self.adapter.register_sensor()

        # register device specific agents
        self.adapter.register_agent(
            sensor_id, sensor_key, "01_Licht", "TimeAgent")
        self.adapter.register_agent(
            sensor_id, sensor_key, "02_Wasser", "ThresholdAgent")
        self.adapter.register_agent(
            sensor_id, sensor_key, "03_PWM", "PercentAgent")

        return (sensor_id, sensor_key)

    def on_agent_cmd(self, agent_index: int, cmd: int):
        '''Converts the recevived i64 into an actual command for the (alpabetically ordered) agent'''
        state = (cmd == 1)
        if agent_index == 0:
            print(f"light: {state}")
            self.light_relay.set_state(state)
        elif agent_index == 1:
            print(f"water: {state}")
            self.water_relay.set_state(state)
        elif agent_index == 2:
            print(f"pwm: {cmd}")
            self.pwm_device.set_speed(cmd)

    def get_sensor_data(self) -> SensorData:
        '''Fetches fres, uncached data from the xiamo sensor'''
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
