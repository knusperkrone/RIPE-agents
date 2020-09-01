#include "access_point.h"

bool AccessPoint::is_enabled;

void AccessPoint::enable() {
    if (AccessPoint::is_enabled) {
        return;
    }
    AccessPoint::is_enabled = true;
    WiFi.softAP(WLAN_SSID, NULL);

    IPAddress IP = WiFi.softAPIP();
    Serial.print("[INFO] AP IP address: ");
    Serial.println(IP);
}

void AccessPoint::disable() {
    AccessPoint::is_enabled = false;
    WiFi.softAPdisconnect();
}
