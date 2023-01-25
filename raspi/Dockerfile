FROM python:3-alpine3.12
# https://github.com/alpinelinux/docker-alpine/issues/135

RUN apk add bluez make gcc libc-dev glib-dev

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ripe.py ripe.py
COPY app app
COPY *.json ./

CMD ["python3", "-u" , "ripe.py"]
