#include "settings.h"

void Settings::setup() {
    *key_str_buffer = 0;
    *id_str_buffer = 0;
    EEPROM.begin(512);
}

int Settings::get_sensor_id() {
    unsigned long canary;
    EEPROM.get(CANARY_OFFSET, canary);
    if (canary == CANARY) {
        int id;
        EEPROM.get(ID_OFFSET, id);
        return id;
    }
    return -1;
}

void Settings::set_sensor_data(int id, char *key) {
    strncpy(key_str_buffer, key, sizeof(key_str_buffer));
    EEPROM.put(CANARY_OFFSET, CANARY);
    EEPROM.put(ID_OFFSET, id);
    EEPROM.put(KEY_OFFSET, key_str_buffer);
    EEPROM.commit();
}

char *Settings::get_sensor_key() {
    unsigned long canary;
    EEPROM.get(CANARY_OFFSET, canary);
    if (canary == CANARY) {
        if (*key_str_buffer == 0) {
            EEPROM.get(KEY_OFFSET, key_str_buffer);
        }
        return key_str_buffer;
    }
    return NULL;
}

const char *Settings::get_sensor_id_str() {
    if (*id_str_buffer == 0) {
        iota(get_sensor_id(), id_str_buffer, sizeof(id_str_buffer));
    }
    return id_str_buffer;
}