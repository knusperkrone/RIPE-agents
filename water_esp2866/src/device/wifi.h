#pragma once

#include <ESP8266WiFi.h>

#include "constants.h"
#include "settings.h"

class Wifi {
   public:
    static bool connect(int tries = 20);
    static bool reconnect_if_necessary();
    static bool hasConnection();
};

extern WiFiClient wifiClient;
extern Settings settings;