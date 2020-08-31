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
    static std::tuple<int, char*> setup();
    static void send_data();

   private:
    static std::tuple<int, char*> register_sensor();
};