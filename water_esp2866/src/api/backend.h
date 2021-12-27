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
    static std::tuple<const char *,int>fetch_mqtt_broker(int tries = 3);
    static void send_sensor_data();

   private:
    static String *commandTopic;
};