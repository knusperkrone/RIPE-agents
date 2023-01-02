#! /bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

docker stop $(docker ps | grep raspi_sensor | cut -f1 -d' ')

docker build . -t raspi_sensor
docker run \
  --restart unless-stopped \
  --net=host --privileged \
  -e "RIPE_LOOP_ROLLBACK_CMD=bash -c 'bluetoothctl power off && bluetoothctl power on'" \
  -e "BASE_URL=http://ripe.knukro.com/api" \
  -e "CONFIG=config.prod.json" \
  raspi_sensor

docker logs -f $(docker ps | grep raspi_sensor | cut -f1 -d' ')