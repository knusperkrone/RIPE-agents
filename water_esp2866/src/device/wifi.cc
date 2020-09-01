#include "wifi.h"

WiFiClient wifiClient;
boolean has_connection;

bool Wifi::connect() {
    if (WiFi.status() == WL_CONNECTED) {
        return true;
    }
    
    WiFi.begin(settings.get_wifi_ssid(), settings.get_wifi_pwd());
    int tries = 20;  // 10 seconds
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        if (tries-- == 0) {
            WiFi.disconnect();
            Serial.println();
            Serial.println("[INFO] WiFi connection failed");
            return false;
        }
    }
    Serial.print("\n");

    Serial.print("[INFO] WiFi connected: ");
    Serial.println(WiFi.localIP());
    has_connection = true;
    return true;
}

bool Wifi::hasConnection() {
    return has_connection;
}

void Wifi::reconnect() {
    if (has_connection && WiFi.status() != WL_CONNECTED) {
        Serial.println("[WARN] Wifi was lost");
        Wifi::connect();
    }
}
