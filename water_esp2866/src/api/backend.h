#pragma once

#include <Arduino.h>
#include <ESP8266HTTPClient.h>

#include "device/mqtt.h"
#include "device/sensors.h"
#include "device/settings.h"
#include "device/wifi.h"
#include "dto.h"

#define KEY_LENGTH 8

class BackendAdapter {
   public:
    static bool setup(int tries = 3);
    static void send_data();

   private:
    static std::tuple<int, const char *> register_sensor();
    static bool register_agent(int id, const char *key, const char *domain, const char *agent);
};