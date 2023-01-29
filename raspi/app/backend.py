import json
from typing import Tuple, Final
import requests as re


class BackendAdapter:
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url: Final[str] = base_url

    def register_sensor(self) -> Tuple[int, str]:
        r = re.post(f'{self.base_url}/sensor', json={})
        sensor_id = r.json()['id']
        sensor_key = r.json()['key']
        return (sensor_id, sensor_key)

    def register_agent(self, sensor_id: int, sensor_key: str, domain: str, agent: str):
        re.post(f'{self.base_url}/agent/{sensor_id}', headers={'X-KEY': sensor_key},
                json={"domain": domain, "agent_name": agent})

    def fetch_sensor_broker(self, sensor_id: int, sensor_key: str) -> str:
        r = re.get(f'{self.base_url}/sensor/{sensor_id}',
                   headers={'X-KEY': sensor_key}, timeout=1000)

        try:
            broker = r.json()['broker']['tcp']
            if broker is None:
                raise RuntimeError(f'No broker returned in {r.text}')
            return broker
        except:
            raise RuntimeError(r.json()['error'])


class SensorData:
    def __init__(self, battery: int, moisture: float, light: int, temperature: float, conductivity: int):
        super().__init__()
        self.battery: Final[int] = battery
        self.moisture: Final[float] = moisture
        self.light: Final[int] = light
        self.temperature: Final[float] = temperature
        self.conductivity: Final[int] = conductivity

    def json(self) -> str:
        return json.dumps({
            'battery': int(self.battery),
            'moisture': float(self.moisture),
            'light': int(self.light),
            'temperature': float(self.temperature),
            'conductivity': int(self.conductivity),
        })

    def get(self, key):
        try:
            return getattr(self, key)
        except:
            return None

    def __str__(self) -> str:
        return self.json()
