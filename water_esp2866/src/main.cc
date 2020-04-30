#include <Arduino.h>
#include <ArduinoJson.h>

#include "api/backend.h"
#include "api/dto.h"
#include "constants.h"
#include "device/mqtt.h"
#include "device/sensors.h"
#include "device/settings.h"
#include "device/wifi.h"

// Init global variables
Settings settings;

void mqtt_callback(char *topic, byte *payload, unsigned int length) {
    char msg[length + 1];
    memccpy(msg, payload, '\0', length);
    msg[length] = '\0';

    DeserializationError error = deserializeJson(cmdMsgBuffer, msg);
    if (error) {
        Serial.println("[ERROR] Failed to deserialize backend response");
    } else {
        const char *domain = cmdMsgBuffer["domain"];
        if (strcmp(domain, SENSOR_WATER_DOMAIN) == 0) {
            Sensor::set_water(cmdMsgBuffer["payload"]);
        }
    }
}

void setup() {
    Serial.begin(9600);

    settings.setup();
    Wifi::connect();

    BackendAdapter::setup();
    Mqtt::setup(mqtt_callback);

    pinMode(WATER_RELAY, OUTPUT);
}

void loop() {
    Wifi::reconnect();            // Refresh wifi_connection - if necessary
    Mqtt::loop();                 // Check for new mqtt messages
    BackendAdapter::send_data();  // Send sensor data - if necessary

    delay(1000);  // Save Battery
}
