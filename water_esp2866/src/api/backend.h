#pragma once

#include <Arduino.h>
#include <ESP8266HTTPClient.h>

#include "device/mqtt.h"
#include "device/sensors.h"
#include "device/settings.h"
#include "device/wifi.h"
#include "dto.h"

class BackendAdapter {
   public:
    static int setup();
    static void send_data();

   private:
    static int fetch_sensor_id();
};