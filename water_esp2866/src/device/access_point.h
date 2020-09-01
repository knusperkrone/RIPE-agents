#pragma once

#include <Arduino.h>
#include <ESP8266WiFi.h>

#include "constants.h"

class AccessPoint {
    static bool is_enabled;

   public:
    static void enable();
    static void disable();
};
