#pragma once

#include <Arduino.h>

#include "constants.h"

class Sensor {
   public:
    static void setup_pins();
    static void set_water(int32_t on);
    static int read_moisture();
};
