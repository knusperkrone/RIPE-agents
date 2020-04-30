#pragma once

#include <Arduino.h>
#include <EEPROM.h>

#include "constants.h"
#include "utils.h"

#define CANARY 0xc0ffe + 1
#define ID_OFFSET 0

struct SensorIdCanary {
    unsigned int canary;
    int id;
};

class Settings {
   public:
    void setup();
    int get_sensor_id();
    void set_sensor_id(int id);
    const char *get_sensor_id_str();

   private:
    char id_str_buffer[8];

    template <typename T>
    static void read(int offset, T &val);
    template <typename T>
    static void write(int offset, T &val);
};

extern Settings settings;
