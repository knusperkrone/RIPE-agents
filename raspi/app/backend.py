import requests as re


class BackendAdapter:
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def register_sensor(self) -> (int, str):
        r = re.post(f'{self.base_url}/sensor', json={})
        sensor_id = r.json()['id']
        sensor_key = r.json()['key']
        return (sensor_id, sensor_key)

    def register_agent(self, sensor_id: int, sensor_key: str, domain: str, agent: str):
        re.post(f'{self.base_url}/agent/{sensor_id}', headers={'X-KEY': sensor_key},
                json={"domain": domain, "agent_name": agent})

    def fetch_sensor_broker(self, sensor_id: int, sensor_key: str) -> str:
        r = re.get(f'{self.base_url}/sensor/{sensor_id}', headers={'X-KEY': sensor_key})
        return r.json()['broker']
