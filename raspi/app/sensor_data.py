import json


class SensorData:
    def __init__(self, battery: int, moisture: float, light: int, temperature: float, conductivity: int):
        super().__init__()
        self.battery = battery
        self.moisture = moisture
        self.light = light
        self.temperature = temperature
        self.conductivity = conductivity

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
