import time

from app.util.log import logger

from .gpio import GPIO, RFDevice
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
        logger.debug(f"{self} enable")

    def disable(self):
        self.active = False
        GPIO.output(self.gpio, GPIO.HIGH)
        logger.debug(f"{self} disable")

    def failsaife(self):
        if self.failsaife_state:
            self.enable()
        else:
            self.disable()
        logger.warn(f"{self} failsafe state is: {self.failsaife_state}")

    def set_state(self, cmd: int):
        if cmd == 1:
            self.enable()
        else:
            self.disable()

    def __str__(self) -> str:
        return f"RelayAgent[{self.gpio}]"


class PwmAgent(Agent):
    def __init__(
        self, name: str, type: str, failsafe: int, gpio_write: int, gpio_control: int
    ):
        super().__init__(name, type, failsafe)
        self.gpio_write = gpio_write
        self.gpio_control = gpio_control

        GPIO.setup(self.gpio_write, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_write, 23)
        self.pwm.start(0)
        self.pwm_speed = 0

    def failsaife(self):
        self.set_state(self.failsaife_state)
        logger.warn(f"{self} failsafe state is: {self.failsaife_state}")

    def set_state(self, speed: int):
        self.pwm_speed = speed
        self.pwm.ChangeDutyCycle(speed)
        logger.debug(f"{self} ChangeDutyCycle {speed}")

    def __str__(self) -> str:
        return f"PwmAgent[{self.gpio_write}:{self.gpio_control}]"


class RfdAgent(Agent):
    devices: dict[int, RFDevice] = {}

    def __init__(
        self, name: str, type: str, failsafe: bool, gpio: int, on: int, off: int
    ):
        super().__init__(name, type, failsafe)
        self.gpio = gpio
        self.on: int = on
        self.off: int = off
        self.device: RFDevice = self._init_device(gpio)

    def failsaife(self):
        if self.failsaife_state:
            self.set_state(1)
        else:
            self.set_state(0)
        logger.warn(f"{self} failsafe state is: {self.failsaife_state}")

    def set_state(self, cmd: int):
        if cmd == 1:
            self._send(self.on)
        else:
            self._send(self.off)

    def _send(self, code: int):
        self.device.tx_code(code)
        logger.debug(f"{self} send {code}")

    def _init_device(self, gpio: int) -> RFDevice:
        if gpio not in RfdAgent.devices:
            logger.info(f"{self} initing RfDevice {gpio}")
            RfdAgent.devices[gpio] = RFDevice(gpio)
            RfdAgent.devices[gpio].enable_tx()
        return RfdAgent.devices[gpio]

    def __str__(self) -> str:
        return f"RfdAgent[{self.gpio}:{self.on}:{self.off}]"
