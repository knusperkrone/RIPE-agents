import requests as re

BASE_URL = 'http://192.168.178.22:8000/api'
# BASE_URL = 'http://ripe.feste-ip.net:35962/api'


def register_sensor() -> (int, str):
    r = re.post(f'{BASE_URL}/sensor', json={})
    sensor_id = r.json()['id']
    sensor_key = r.json()['key']
    return (sensor_id, sensor_key)


def register_agent(sensor_id: int, sensor_key: str, domain: str, agent: str):
    re.post(f'{BASE_URL}/agent/{sensor_id}', headers={'X-KEY': sensor_key},
                json={"domain": domain, "agent_name": agent})


def fetch_sensor_broker(sensor_id: int, sensor_key: str) -> str:
    return re.get(f'{BASE_URL}/sensor/{sensor_id}', headers={'X-KEY': sensor_key}).json()['broker']
