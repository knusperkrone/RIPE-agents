FROM python:3-alpine3.12
# https://github.com/alpinelinux/docker-alpine/issues/135

RUN apk add make gcc libc-dev glib-dev && \
    pip3 install paho-mqtt miflora bluepy btlewrap requests

WORKDIR /app
COPY . /app

CMD ["python3", "-u" , "ripe.py"]