#pragma once

#include <Arduino.h>
#include <EEPROM.h>

#include "constants.h"
#include "utils.h"

#define CANARY (unsigned long)0xc0ffee + 10

#define SENSOR_CANARY_OFFSET 0
#define ID_OFFSET SENSOR_CANARY_OFFSET + sizeof(unsigned long)
#define KEY_OFFSET ID_OFFSET + sizeof(unsigned long)
#define WIFI_CANARY_OFFSET KEY_OFFSET + 12
#define SSID_OFFSET WIFI_CANARY_OFFSET + sizeof(unsigned long)
#define PWD_OFFSET SSID_OFFSET + 36
#define XXX_OFFSET PWD_OFFSET + 64

class Settings {
   public:
    void setup();
    bool set_sensor_config(int id, const char *key);
    bool set_wifi_config(const char *ssid, const char *pwd);
    int get_sensor_id();
    const char *get_sensor_key();
    const char *get_sensor_id_str();
    const char *get_wifi_ssid();
    const char *get_wifi_pwd();

   private:
    char id_str_buffer[8];
    char key_str_buffer[9];
    char ssid_str_buffer[36];
    char pwd_str_buffer[64];
};

extern Settings settings;
