import os
import time as t

from .util.log import logger
from .backend import BackendAdapter
from .device import Device
from .mqtt import MqttContext


def kickoff(base_url):
    adapter = BackendAdapter(base_url)
    device = Device(adapter)

    rollback_cmd = os.environ.get('RIPE_LOOP_ROLLBACK_CMD')
    if rollback_cmd:
        logger.info(f'Rollback cmd: {rollback_cmd}')
    else:
        logger.info(f'No rollback cmd')

    sensor_id, sensor_key = device.get_creds()

    mqtt_context = MqttContext(adapter, device, sensor_id, sensor_key)
    mqtt_context.connect()

    while True:
        try:
            payload = device.get_sensor_data()
            
            if not mqtt_context.is_connected():
                mqtt_context.connect()
            mqtt_context.publish(payload)
            mqtt_context.log("published sensordata")
        except Exception as e:
            # Rollback logic
            if rollback_cmd is not None:
                rollback_succeeded = os.system(rollback_cmd) == 0
                mqtt_context.log(
                    f"Failed publishing due {e.__class__}, rollback succeeded: {rollback_succeeded}")
                if rollback_succeeded:
                    t.sleep(10)
                    continue
            else:
                mqtt_context.log(f"Failed publishing {e.__class__}")

        # timeout
        t.sleep(120)
