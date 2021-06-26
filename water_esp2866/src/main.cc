#include <Arduino.h>
#include <ArduinoJson.h>

#include "api/backend.h"
#include "api/dto.h"
#include "api/offline_agent.h"
#include "api/server.h"
#include "constants.h"
#include "device/access_point.h"
#include "device/mqtt.h"
#include "device/sensors.h"
#include "device/settings.h"
#include "device/wifi.h"

// Init global variables
Settings settings;
static bool is_online;
static bool wifi_settings_updated;

void mqtt_callback(char *topic, byte *payload, unsigned int length) {
    // Each command has a int32_t payload
    int32_t *commands = (int32_t *)payload;
    for (size_t i = 0; i < sizeof(AGENTS) / sizeof(AGENTS[0]); i++) {
        AGENTS[i].callback(commands[i]);
    }
}

void server_teardown_callback() {
    // Server is shuting down
    AccessPoint::disable();
}

void server_config_callback(const char *ssid, const char *pwd) {
    // Server received message
    if (settings.set_wifi_config(ssid, pwd)) {
        Serial.println("[INFO] Saved new wifi config");
        wifi_settings_updated = true;  // Seems to be ISR context, so notfiy main thread
    } else {
        Serial.println("[ERROR] failed storing ssid and pwd");
    }
}

void setup() {
    Serial.begin(9600);
    delay(100);
    pinMode(WATER_RELAY, OUTPUT);
    delay(100);

    settings.setup();
    // Check if we have wifi connection
    is_online = Wifi::connect() && BackendAdapter::setup();
    if (is_online) {
        Mqtt::setup(mqtt_callback);
    } else {
        // Wind up accessPoint with server
        AccessPoint::enable();
        ConfigServer::start(server_config_callback, server_teardown_callback);
        OfflineAgent::setup();
    }
}

void check_settings_updated() {
    if (wifi_settings_updated) {
        Serial.println("[INFO] Main-thread is updating settings");
        wifi_settings_updated = false;

        is_online = Wifi::connect() && BackendAdapter::setup();
        if (is_online) {
            ConfigServer::end();
            Mqtt::setup(mqtt_callback);
            OfflineAgent::stop();
        } else {
            // try again..
            AccessPoint::enable();
            ConfigServer::start(server_config_callback, server_teardown_callback);
            OfflineAgent::setup();
        }
    }
}

void loop() {
    check_settings_updated();

    if (is_online) {
        Wifi::reconnect();            // Refresh wifi_connection - if necessary
        Mqtt::loop();                 // Check for new mqtt messages
        BackendAdapter::send_data();  // Send sensor data - if necessary
        delay(1000);                  // Stay responsive
    } else {
        OfflineAgent::loop();
        ConfigServer::loop();  // Disable AP after a few minutes
        delay(5000);           // Stay not so responsive - better battery
    }
}
