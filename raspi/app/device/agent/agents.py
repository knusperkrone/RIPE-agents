import time

from app.util.log import logger

from .gpio import GPIO
from .base import Agent


class RelayAgent(Agent):
    def __init__(self, name: str, type: str, failsafe: bool, gpio: int):
        super().__init__(name, type, failsafe)
        self.gpio = gpio
        GPIO.setup(self.gpio, GPIO.OUT)
        time.sleep(0.1)
        self.disable()

    def enable(self):
        self.active = True
        GPIO.output(self.gpio, GPIO.LOW)

    def disable(self):
        self.active = False
        GPIO.output(self.gpio, GPIO.HIGH)

    def failsaife(self):
        if self.failsaife_state:
            self.enable()
        else:
            self.disable()
        logger.warn(f'{self} failsafe state is: {self.failsaife_state}')

    def set_state(self, cmd: int):
        if cmd == 1:
            self.enable()
        else:
            self.disable()

    def __str__(self) -> str:
        return f'RelayAgent[{self.gpio}]'


class PwmAgent(Agent):
    def __init__(self, name: str, type: str, failsafe: int, gpio_write: int, gpio_control: int):
        super().__init__(name, type, failsafe)
        self.gpio_write = gpio_write
        self.gpio_control = gpio_control

        GPIO.setup(self.gpio_write, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_write, 23)
        self.pwm.start(0)
        self.pwm_speed = 0

    def failsaife(self):
        self.set_state(self.failsaife_state)
        logger.warn(f'{self} failsafe state is: {self.failsaife_state}')

    def set_state(self, speed: int):
        self.pwm_speed = speed
        self.pwm.ChangeDutyCycle(speed)

    def __str__(self) -> str:
        return f'PwmAgent[{self.gpio_write}:{self.gpio_control}]'


def create_agent_from_json(json) -> Agent:
    type = json['type']
    if type == 'relay':
        return RelayAgent(
            json['name'],
            type,
            json['failsafe'],
            json['gpio'],
        )
    elif type == 'pwm':
        return PwmAgent(
            json['name'],
            type,
            json['failsafe'],
            json['gpio']['write'],
            json['gpio']['control'],
        )
    else:
        raise NotImplementedError(f'Invalid agent-type: {type}')
