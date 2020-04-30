#include "wifi.h"

WiFiClient wifiClient;

void Wifi::connect() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }
    Serial.println("[INFO ]Connecting to ");
    Serial.println(SSID_NAME);

    WiFi.begin(SSID_NAME, SSID_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.print("\n");

    Serial.print("[INFO] WiFi connected: ");
    Serial.println(WiFi.localIP());
}

void Wifi::reconnect() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[WARN] Wifi was lost");
        Wifi::connect();
    }
}
