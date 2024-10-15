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
    mqtt_context.kickoff()

    if rollback_cmd is not None:
        rollback_succeeded = os.system(rollback_cmd) == 0
        logger.info(f"Initial rollback succeeded: {rollback_succeeded}")

    while not mqtt_context.is_connected():
        logger.info("Waiting for mqtt connection")
        await asyncio.sleep(1)

    while True:
        try:
            if not mqtt_context.is_connected():
                logger.warning("Mqtt not connected - skipping")
            else:
                payload = await asyncio.wait_for(device.get_sensor_data(), timeout=90.0)

                await mqtt_context.publish(payload)
                await mqtt_context.log("published sensordata")
        except asyncio.TimeoutError:
            await mqtt_context.log(f"Bluetooth timeout, retrying in 120 seconds")
        except Exception as e:
            # Rollback logic
            print(e)
            if rollback_cmd is not None:
                rollback_succeeded = os.system(rollback_cmd) == 0
                await mqtt_context.log(
                    f"Failed publishing due {e.__class__}, rollback succeeded: {rollback_succeeded}"
                )
                if rollback_succeeded:
                    await asyncio.sleep(120)
                    continue
            else:
                await mqtt_context.log(f"Failed publishing {e.__class__}")

        # timeout
        await asyncio.sleep(60)
