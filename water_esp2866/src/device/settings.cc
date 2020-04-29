#include "settings.h"

void settings_setup() {
    EEPROM.begin(512);
}

int get_sensor_id() {
    SensorIdCanary canary;
    EEPROM.get(ID_OFFSET, canary);
    if (canary.canary == CANARY) {
        return canary.id;
    }
    return -1;
}

void set_sensor_id(int id) {
    SensorIdCanary canary = {
        canary : CANARY,
        id : id,
    };
    EEPROM.put(ID_OFFSET, canary);
    if (!EEPROM.commit()) {
        Serial.println("[ERROR] Invalid EEPROM write!");
    }
}

char *get_sensor_id_str() {
    static char buffer[12];
    if (*buffer == 0) {
        iota(get_sensor_id(), buffer, sizeof(buffer));
    }
    return buffer;
}