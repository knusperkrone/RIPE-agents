#! /bin/bash

RIPE_LOOP_ROLLBACK_CMD="bash -c 'bluetoothctl power off && bluetoothctl power on'"
BASE_URL=http://ripe.knukro.com/api
while true; do
    python3 ./ripe.py
    sleep 1
done;