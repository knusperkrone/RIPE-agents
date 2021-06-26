#include "offline_agent.h"

#include <Arduino.h>

#include "device/sensors.h"

#define MIN_MOISTURE 15
#define WATERING_MS 1000 * 30
#define WATERING_HOLD_MS 1000 * 60 * 30

long OfflineAgent::last_watered;
bool OfflineAgent::active;

void OfflineAgent::setup() {
    OfflineAgent::last_watered = 0;
    OfflineAgent::active = false;
}

void OfflineAgent::loop() {
    long delta = millis() - OfflineAgent::last_watered;
    if (OfflineAgent::active && delta > WATERING_MS) {
        OfflineAgent::stop();
    } else if (!OfflineAgent::active && delta > WATERING_HOLD_MS && Sensor::read_moisture() < MIN_MOISTURE) {
        OfflineAgent::active = true;
        OfflineAgent::last_watered = millis();
        Sensor::set_water(true);
    }
}

void OfflineAgent::stop() {
    if (OfflineAgent::active) {
        Sensor::set_water(false);
        OfflineAgent::active = false;
        OfflineAgent::last_watered = millis();
    }
}