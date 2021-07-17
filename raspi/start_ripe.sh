#! /bin/bash

docker build . -t raspi_sensor
docker run -d --restart unless-stopped --net=host --privileged -e "BASE_URL=http://192.168.178.37:8080/api" raspi_sensor