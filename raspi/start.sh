#! /bin/bash

while true; do
	kill -9 $(lsof -t -i :1883) > /dev/null  2>&1
	if [ $? -ne 0 ]; then
		python3 -u main.py
	fi
done
