class DebugPWM:
    def __init__(self, gpio_write, hz):
        print(f'\033[96mPWM: {gpio_write} - {hz}\033[0m')

    def start(self, param):
        print(f'\033[96mPWM start: {param}\033[0m')

    def ChangeDutyCycle(self, speed):
        print(f'\033[96mPWM ChangedutyCycle: {speed}\033[0m')


class GPIO:

    LOW = 'LOW'
    HIGH = 'HIGH'
    BOARD = 'BOARD'
    OUT = 'OUT'
    IN = 'IN'
    BCM = 'BCM'

    @staticmethod
    def setmode(a):
        print(f'\033[96msetmode: {a}\033[0m')

    @staticmethod
    def setup(a, b):
        print(f'\033[96msetup: {a}, {b}\033[0m')

    @staticmethod
    def output(a, b):
        print(f'\033[96mOutput: {a}, {b}\033[0m')

    @staticmethod
    def cleanup():
        print(f'\033[96mcleanup\033[0m')

    @staticmethod
    def setwarnings(flag):
        print(f'\033[96msetwarnings: {flag}\033[0m')

    @staticmethod
    def PWM(gpio_write, param) -> DebugPWM:
        return DebugPWM(gpio_write, param)
