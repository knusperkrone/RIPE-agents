import json


class SensorData:
    def __init__(self, battery: int, moisture: float, light: float, temperature: float, conductivity: float):
        super().__init__()
        self.battery = battery
        self.moisture = moisture
        self.light = light
        self.temperature = temperature
        self.conductivity = conductivity

    def SensorData(self) -> str:
        return json.dumps({
            'battery': self.battery,
            'moisture': self.moisture,
            'light': self.light,
            'temperature': self.temperature,
            'conductivity': self.conductivity,
        })
