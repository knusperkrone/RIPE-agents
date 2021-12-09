# RIPE on the  ESP32 nodemcu

Brings the RIPE protocoll to the raspberry pi.

This implementation supports a Water/Light and PWM device.

The sensor data is minded via a `MiFlora` sensor.

## Development

Install the requirements via `pip install -r requirements.txt` and run `python3 ./ripe.py`.

## Flash your own

Install docker an run `./start_ripe.sh` to run it as daemon.

## Customize

One needs to customize the the pythoncode.

1. Delete `config.json` to register a new sensor
2. Edit `device.py:register_backend` and a new [Agent](http://retroapp.if-lab.de:8000/api/agent)
3. Customize the `device.py:on_agent_cmd` method to match the order of the command bytes
4. To send new sensor data to the backend one needs to edit `device.py:get_sensor_data`
