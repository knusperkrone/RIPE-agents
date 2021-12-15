# RIPE on the  ESP32 Nodemcu

Bring the RIPE protocol to your Nodemcu.

Currently, only watering is supported.

The moisture data is fetched with a `Moisture Sensor v1.2`

## Development

Install [Platformio Core](https://docs.platformio.org/en/latest/what-is-platformio.html) and execute `./build.sh`

## Flash your own

Execute `./build.sh register`.
This will register a new Sensor and flashes the credentials on your ESP32.

One can read the credentials in the last line of the executed command.

After that, the sensor can get controlled via the RIPE app.

## Customize

One needs to customize the backend and the Nodemcus user code.

1. Alter the `register.py` for adding a new agent. See [here](http://retroapp.if-lab.de:8000/api/agent), which agents are currently supported
2. Edit the `main.cc::mqtt_callback` function to access the command bytes
3. If one adds a new sensor(metric), this is done in `backend.cc::send_sensor_data`, just customize the JSON
