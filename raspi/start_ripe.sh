#! /bin/bash

docker build . -t raspi_sensor
docker run -d --restart unless-stopped --net=host --privileged -e "BASE_URL=http://retroapp.if-lab:8000/api" raspi_sensor
