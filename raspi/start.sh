#! /bin/bash

while true; do
	kill -9 $(lsof -t -i :1883)
	python3 -u main.py
done
