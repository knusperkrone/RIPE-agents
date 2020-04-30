#pragma once

#include <ESP8266WiFi.h>

#include "constants.h"

class Wifi {
   public:
    static void connect();
    static void reconnect();
};

extern WiFiClient wifiClient;