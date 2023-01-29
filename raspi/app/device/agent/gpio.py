import time
import io

from app.util.log import logger


class MockPWM:
    def __init__(self, gpio_write, hz):
        logger.debug(f'PWM: {gpio_write} - {hz}')

    def start(self, param):
        logger.debug(f'PWM start: {param}')

    def ChangeDutyCycle(self, speed):
        logger.debug(f'PWM ChangedutyCycle: {speed}')


class MockGPIO:

    LOW = 'LOW'
    HIGH = 'HIGH'
    BOARD = 'BOARD'
    OUT = 'OUT'
    IN = 'IN'
    BCM = 'BCM'

    @staticmethod
    def setmode(a):
        logger.debug(f'setmode: {a}')

    @staticmethod
    def setup(a, b):
        logger.debug(f'setup: {a}, {b}')

    @staticmethod
    def output(a, b):
        logger.debug(f'Output: {a}, {b}')

    @staticmethod
    def cleanup():
        logger.debug(f'cleanup')

    @staticmethod
    def setwarnings(flag):
        logger.debug(f'setwarnings: {flag}')

    @staticmethod
    def PWM(gpio_write, param) -> MockPWM:
        return MockPWM(gpio_write, param)


try:
    import RPi.GPIO as GPIO

    GPIO.setwarnings(False)
    GPIO.cleanup()
    time.sleep(0.1)
    GPIO.setmode(GPIO.BCM)

    logger.info('Loaded GPIOs for Raspberry Pi')
except ModuleNotFoundError as e:
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                logger.critical('Failed to load RPi.GPIO on Raspberry Pi')
                raise e
    except Exception:
        pass

    logger.warn('Mocking GPIO on uknown machine')
    from .gpio import MockGPIO as GPIO
    from .gpio import MockPWM as PWM
