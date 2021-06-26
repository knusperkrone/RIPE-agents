

class GPIO:

    LOW = 'LOW'
    HIGH = 'HIGH'
    BOARD = 'BOARD'
    OUT = 'OUT'
    IN = 'IN'
    BCM = 'BCM'

    @staticmethod
    def setmode(a):
        print(f'setmode: {a}')

    @staticmethod
    def setup(a, b):
        print(f'setup: {a}, {b}')

    @staticmethod
    def output(a, b):
        print(f'Output: {a}, {b}')

    @staticmethod
    def cleanup():
        print(f'cleanup')

    def setwarnings(flag):
        print(f'setwarnings: {flag}')


class DebugPWM:
    def __init__(self, gpio_write, hz):
        print(f'PWM: {gpio_write} - {hz}')

    def start(self, param):
        print(f'PWM start: {param}')

    def ChangeDutyCycle(self, speed):
        print(f'PWM ChangedutyCycle: {speed}')


def PWM(gpio_write, param) -> DebugPWM:
    return DebugPWM(gpio_write, param)
