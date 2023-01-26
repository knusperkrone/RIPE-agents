import io
import time

try:
    import RPi.GPIO as GPIO

    GPIO.setwarnings(False)
    GPIO.cleanup()
    time.sleep(0.1)
    GPIO.setmode(GPIO.BCM)

    print('''\033[91mLoaded GPIOs for Raspberry Pi\033[0m''')
except ModuleNotFoundError as e:
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                print(
                    '''\033[91mFailed to load RPi.GPIO on Raspberry Pi\033[0m''')
                raise e
    except Exception:
        pass

    print('''\033[91mMocking GPIO\033[0m''')
    from .mock_gpio import GPIO
