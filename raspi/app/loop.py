import os
import asyncio
import subprocess
import time as t

from .util.log import logger
from .util.config import CONFIG
from .backend import BackendAdapter
from .device import Device
from .mqtt import MqttContext


def get_git_hash():
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except:
        return "0000000"


async def kickoff():
    version = get_git_hash()
    base_url = CONFIG.base_url
    adapter = BackendAdapter(base_url)
    device = Device(adapter)

    rollback_cmd = CONFIG.rollback_cmd
    if rollback_cmd:
        logger.info(f"Rollback cmd: {rollback_cmd}")
    else:
        logger.info(f"No rollback cmd")

    sensor_id, sensor_key = device.get_creds()

    mqtt_context = MqttContext(adapter, device, sensor_id, sensor_key, version)
    asyncio.create_task(mqtt_context.kickoff())

    while True:
        try:
            async with asyncio.timeout(120):
                payload = await device.get_sensor_data()

            await mqtt_context.publish(payload)
            await mqtt_context.log("published sensordata")
        except asyncio.TimeoutError:
            mqtt_context.log(f"Bluetooth timeout, retrying in 120 seconds")
        except Exception as e:
            # Rollback logic
            print(e)
            if rollback_cmd is not None:
                rollback_succeeded = os.system(rollback_cmd) == 0
                await mqtt_context.log(
                    f"Failed publishing due {e.__class__}, rollback succeeded: {rollback_succeeded}"
                )
                if rollback_succeeded:
                    t.sleep(10)
                    continue
            else:
                await mqtt_context.log(f"Failed publishing {e.__class__}")

        # timeout
        t.sleep(120)
