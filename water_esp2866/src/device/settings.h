#pragma once

#include <Arduino.h>
#include <EEPROM.h>

#include "constants.h"
#include "utils.h"

#define CANARY 0xc0ffe
#define ID_OFFSET 0

struct SensorIdCanary {
    unsigned int canary;
    int id;
};

void settings_setup();
int get_sensor_id();
void set_sensor_id(int id);
char *get_sensor_id_str();
