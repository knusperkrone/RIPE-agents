#include "wifi.h"

WiFiClient wifiClient;
int last_reconnect_ms = 0;

bool Wifi::connect(int tries) {
    Serial.print("[INFO] WiFi '");
    Serial.print(settings.get_wifi_ssid());
    Serial.print("' connecting ");
    WiFi.begin(settings.get_wifi_ssid(), settings.get_wifi_pwd());

    while (!Wifi::hasConnection()) {
        delay(500);
        Serial.print(".");
        if (tries-- <= 0) {
            WiFi.disconnect();
            Serial.println();
            Serial.print("[INFO] WiFi connection failed [");
            Serial.print(WiFi.status());
            Serial.println("]");
            return false;
        }
    }
    Serial.print("\n");

    Serial.print("[INFO] WiFi connected: ");
    Serial.println(WiFi.localIP());
    return true;
}

bool Wifi::hasConnection() {
    return WiFi.status() == WL_CONNECTED;
}

bool Wifi::reconnect_if_necessary() {
    if (Wifi::hasConnection()) {
        return false;
    }

    int curr_ms = millis();
    if (curr_ms - last_reconnect_ms > RETRY_TIMEOUT_MS) {
        last_reconnect_ms = curr_ms;
        Serial.println("[INFO] Retrying WiFi connection");
        return Wifi::connect();
    }
    return false;
}
