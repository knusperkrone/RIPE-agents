#! /usr/bin/python
import requests as r

BASE_URL = 'https://retroapp.if-lab.de:8000'

# register sensor
resp_json = r.post(f'{BASE_URL}/api/sensor', json={}).json()
sensor_id = resp_json['id']
sensor_key = resp_json['key']

# register agent
resp_json = r.post(f'{BASE_URL}/api/agent/{sensor_id}', headers={'X-KEY': sensor_key}, json={
    'domain': '01_Water',
    'agent_name': 'ThresholdAgent'
})


print(f'-DSENSOR_ID={sensor_id} -DSENSOR_KEY=\'"{sensor_key}"\'')
