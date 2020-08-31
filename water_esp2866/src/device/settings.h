#pragma once

#include <Arduino.h>
#include <EEPROM.h>

#include "constants.h"
#include "utils.h"

#define CANARY 0xc0ffeeUL + 2

#define CANARY_OFFSET 0
#define ID_OFFSET CANARY_OFFSET + sizeof(unsigned long)
#define KEY_OFFSET ID_OFFSET + sizeof(unsigned long)

class Settings {
   public:
    void setup();
    void set_sensor_data(int id, char *key);
    int get_sensor_id();
    char *get_sensor_key();
    const char *get_sensor_id_str();    

   private:
    char id_str_buffer[8];
    char key_str_buffer[9];
};

extern Settings settings;
