#! /bin/bash

cd $(dirname $0)

export RIPE_LOOP_ROLLBACK_CMD="bash -c 'bluetoothctl power off && bluetoothctl power on'"
export BASE_URL=http://ripe.knukro.com/api
export CONFIG=config.prod.json

while true; do
    python3 ./ripe.py
    sleep 1
done;
