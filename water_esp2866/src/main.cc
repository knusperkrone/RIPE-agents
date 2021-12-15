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
static bool isOnline;
static bool isWifiSettingUpdated;

void mqtt_callback(char *topic, byte *payload, unsigned int length) {
    // Each command has a byte payload
    Sensor::set_water(payload[0]);
}

void server_teardown_callback() {
    AccessPoint::disable();  // Server is shutting down
}

void server_config_callback(const char *ssid, const char *pwd) {
    // Server processed a messagein
    if (settings.set_wifi_config(ssid, pwd)) {
        Serial.println("[INFO] Saved new wifi config");
        isWifiSettingUpdated = true;  // Seems to be ISR context, so notfiy main thread
    } else {
        Serial.println("[ERROR] failed storing ssid and pwd");
    }
}

void connect_mqtt() {
    std::tuple<const char *, int> brokerTuple = BackendAdapter::fetch_mqtt_broker();
    const char *broker = std::get<0>(brokerTuple);
    int port = std::get<1>(brokerTuple);

    Mqtt::setup(mqtt_callback, broker, port);
}

void setup() {
    Serial.begin(9600);
    Sensor::setup_pins();

    settings.setup();
    // Check if we have wifi connection
    isOnline = Wifi::connect() && BackendAdapter::setup();
    if (isOnline) {
        connect_mqtt();
    } else {
        // Wind up accessPoint with server
        AccessPoint::enable();
        ConfigServer::start(server_config_callback, server_teardown_callback);
        OfflineAgent::setup();
    }
}

void check_settings_updated() {
    if (!isWifiSettingUpdated) {
        return;
    }

    Serial.println("[INFO] Main-thread is updating settings");
    isWifiSettingUpdated = false;

    isOnline = Wifi::connect() && BackendAdapter::setup();
    if (isOnline) {
        ConfigServer::end();
        connect_mqtt();
        OfflineAgent::stop();
    } else {
        // try again..
        AccessPoint::enable();
        ConfigServer::start(server_config_callback, server_teardown_callback);
        OfflineAgent::setup();
    }
}

void loop() {
    isWifiSettingUpdated = Wifi::reconnect_if_necessary();
    check_settings_updated();

    if (isOnline) {
        Mqtt::loop();                        // Check for new mqtt messages
        BackendAdapter::send_sensor_data();  // Send sensor data
        delay(1500);                         // Stay responsive
    } else {
        OfflineAgent::loop();
        ConfigServer::loop();  // Disable AP after a few minutes
        delay(5000);           // Stay not so responsive
    }
}
