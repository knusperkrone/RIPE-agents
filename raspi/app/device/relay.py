'''
Extend GPIO.HIGH and GPIO.LOW with some bool logic semantics with OOP
'''
import time

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    from .mock_gpio import GPIO


class RelayDevice:

    def __init__(self, gpio: int):
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

    def set_state(self, active: bool):
        if active:
            self.enable()
        else:
            self.disable()
