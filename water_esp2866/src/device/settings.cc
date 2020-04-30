#include "settings.h"

void Settings::setup() {
    EEPROM.begin(512);
}

int Settings::get_sensor_id() {
    SensorIdCanary canary;
    Settings::read(ID_OFFSET, canary);
    if (canary.canary == CANARY) {
        return canary.id;
    }
    return -1;
}

void Settings::set_sensor_id(int id) {
    SensorIdCanary canary = {
        canary : CANARY,
        id : id,
    };
    Settings::write(ID_OFFSET, canary);
}

const char *Settings::get_sensor_id_str() {
    if (*this->id_str_buffer == 0) {
        iota(this->get_sensor_id(), id_str_buffer, sizeof(this->id_str_buffer));
    }
    return id_str_buffer;
}

template <typename T>
void Settings::read(int offset, T &val) {
    EEPROM.get(offset, val);
}

template <typename T>
void Settings::write(int offset, T &val) {
    EEPROM.put(offset, val);
    if (!EEPROM.commit()) {
        Serial.println("[ERROR] Invalid EEPROM write!");
    }
}
