#pragma once

#include <Arduino.h>

#include "constants.h"

class Sensor {
   public:
    static void set_water(bool on);
    static int read_moisture();
};
