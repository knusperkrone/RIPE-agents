#include "sensors.h"

void Sensor::set_water(int32_t on) {
    if (on) {
        Serial.println("[INFO] Water on");
        digitalWrite(WATER_RELAY, HIGH);
    } else {
        Serial.println("[INFO] Water off");
        digitalWrite(WATER_RELAY, LOW);
    }
}

int Sensor::read_moisture() {
    int moisture = analogRead(MOISTURE_SENSOR);

    // Absolute measured values
    int max = 870;
    int min = 440;
    // Normalize
    moisture -= min;
    max -= min;
    // Rule of three
    moisture *= 100;
    moisture /= max;
    moisture = 100 - moisture;
    if (moisture > 100) {
        moisture = 100;
    } else if (moisture < 0) {
        moisture = 0;
    }

    return moisture;
}