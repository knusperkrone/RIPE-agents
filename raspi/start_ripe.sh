#! /bin/bash

docker build . -t raspi_sensor
docker run -d --restart unless-stopped --net=host --privileged -e "BASE_URL=http://ripe.knukro.com/api" raspi_sensor
