#! /usr/bin/bash
set -e

if [[ $1 = 'register' ]]; then
    ./register.py > tmp.values
    platformio run -e register -t upload
    cat tmp.values
    rm tmp.values
else
    platformio run -e debug -t upload && \
        platformio device monitor
fi
