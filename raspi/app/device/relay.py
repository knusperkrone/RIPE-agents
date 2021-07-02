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

class PWMDevice:

    def __init__(self, gpio_write: int, gpio_control: int):
        GPIO.setmode(GPIO.BCM)
        self.gpio_write = gpio_write
        self.gpio_control = gpio_control
        GPIO.setup(self.gpio_write, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_write, 23)
        self.pwm.start(0)
        self.pwm_speed = 0

    def set_speed(self, speed: int):
        self.pwm_speed = speed
        self.pwm.ChangeDutyCycle(speed)
