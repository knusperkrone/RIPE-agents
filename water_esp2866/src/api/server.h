#pragma once

#include <ArduinoJson.h>
#include <AsyncJson.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>

#include "constants.h"

class ConfigServer {
   public:
    static void start(void (*connect_callback)(const char *,const char *), void (*teardown_callback)());
    static void loop();
    static void end();
};

extern ConfigServer configServer;