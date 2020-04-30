#include <Arduino.h>
#include <ArduinoJson.h>

#include "api/backend.h"
#include "api/dto.h"
#include "constants.h"
#include "device/mqtt.h"
#include "device/sensors.h"
#include "device/settings.h"
#include "device/wifi.h"

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
            set_water(cmdMsgBuffer["payload"]);
        }
    }
}

void setup() {
    Serial.begin(9600);

    settings_setup();
    wifi_setup();

    backend_register();
    mqtt_setup(mqtt_callback);

    pinMode(WATER_RELAY, OUTPUT);
}

void loop() {
    wifi_setup();     // Refresh wifi_connection - if necessary
    mqtt_loop();      // Check for new mqtt messages
    send_moisture();  // Send sensor data - if necessary

    delay(1000);  // Save Battery
}
