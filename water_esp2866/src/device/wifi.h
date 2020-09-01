#pragma once

#include <ESP8266WiFi.h>

#include "constants.h"
#include "settings.h"

class Wifi {
   public:
    static bool connect();
    static void reconnect();
    static bool hasConnection();
};

extern WiFiClient wifiClient;
extern Settings settings;