#! /bin/bash

while true; do
    kill $(pgrep -f ripe | grep -v ^$$\$) > /dev/null 2>&1
    python3 -u ripe.py http://192.168.178.37:8080/api
done
