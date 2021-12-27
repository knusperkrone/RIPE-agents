#include "sensors.h"

void Sensor::setup_pins() {
    delay(100);
    pinMode(WATER_RELAY, OUTPUT);
    set_water(false);
    delay(100);
}

void Sensor::set_water(int32_t on) {
    if (on) {
        Serial.println("[INFO] Water on");
        digitalWrite(WATER_RELAY, LOW);
    } else {
        Serial.println("[INFO] Water off");
        digitalWrite(WATER_RELAY, HIGH);
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