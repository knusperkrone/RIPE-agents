FROM python:3-alpine3.12
# https://github.com/alpinelinux/docker-alpine/issues/135

RUN apk add make gcc libc-dev glib-dev && \
    pip3 install paho-mqtt miflora bluepy btlewrap requests pyserial RPi.GPIO

WORKDIR /app
COPY ripe.py ripe.py
COPY app app
COPY *.json ./

CMD ["python3", "-u" , "ripe.py"]
