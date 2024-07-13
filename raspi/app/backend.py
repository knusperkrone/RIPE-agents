import json
from dataclasses import dataclass
from typing import Optional, Tuple, Final
import requests as re # type: ignore


class SensorData:
    def __init__(
        self,
        battery: Optional[int] = None,
        moisture: Optional[float] = None,
        light: Optional[int] = None,
        temperature: Optional[float] = None,
        conductivity: Optional[int] = None,
        humidity: Optional[float] = None,
    ):
        super().__init__()
        self.battery: Final[Optional[int]] = battery
        self.moisture: Final[Optional[float]] = moisture
        self.light: Final[Optional[int]] = light
        self.temperature: Final[Optional[float]] = temperature
        self.conductivity: Final[Optional[int]] = conductivity
        self.humidity: Final[Optional[float]] = humidity

    def json(self) -> str:
        return json.dumps(
            {
                "battery": self.battery,
                "moisture": self.moisture,
                "light": self.light,
                "temperature": self.temperature,
                "conductivity": self.conductivity,
                "humidity": self.humidity,
            }
        )

    def get(self, key):
        try:
            return getattr(self, key)
        except:
            return None

    def __str__(self) -> str:
        return self.json()


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class Broker:
    scheme: str
    host: str
    port: int
    credentials: Optional[Credentials] = None

    def __post_init__(self):
        if self.credentials is not None:
            self.credentials = Credentials(**self.credentials)

    def __str__(self) -> str:
        cred_str = "with" if self.credentials else "without"
        return f"{self.scheme}://{self.host}:{self.port} {cred_str} Credentials"


class BackendAdapter:
    def __init__(self, base_url: str):
        super().__init__()
        print(f"Using base url {base_url}")
        self.base_url: Final[str] = base_url

    def register_sensor(self) -> Tuple[int, str]:
        r = re.post(f"{self.base_url}/sensor", json={})
        sensor_id = r.json()["id"]
        sensor_key = r.json()["key"]
        return (sensor_id, sensor_key)

    def register_agent(self, sensor_id: int, sensor_key: str, domain: str, agent: str):
        re.post(
            f"{self.base_url}/agent/{sensor_id}",
            headers={"X-KEY": sensor_key},
            json={"domain": domain, "agent_name": agent},
        )

    def fetch_sensor_brokers(self, sensor_id: int, sensor_key: str) -> list[Broker]:
        r = re.get(
            f"{self.base_url}/sensor/{sensor_id}",
            headers={"X-KEY": sensor_key},
            timeout=1000,
        )

        try:
            brokers = list(map(lambda x: Broker(**x), r.json()["broker"]["items"]))
            if brokers is None or len(brokers) == 0:
                raise RuntimeError(f"No broker returned in {r.text}")
            return brokers
        except:
            raise RuntimeError(r.json()["error"])
