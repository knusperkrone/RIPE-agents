#include "settings.h"

void Settings::setup() {
    static_assert(XXX_OFFSET < 512, "Memory buffer is larger than the EEPROM");

    *id_str_buffer = 0;
    *ssid_str_buffer = 0;
    *pwd_str_buffer = 0;
    EEPROM.begin(512);
}

bool Settings::set_wifi_config(const char *ssid, const char *pwd) {
    if (strlen(ssid) + 1 > sizeof(ssid_str_buffer) || strlen(pwd) + 1 > sizeof(pwd_str_buffer)) {
        Serial.println("[ERROR] cannot save wifi config");
        return false;
    }
    strcpy(ssid_str_buffer, ssid);
    strcpy(pwd_str_buffer, pwd);

    EEPROM.put(WIFI_CANARY_OFFSET, CANARY);
    EEPROM.put(SSID_OFFSET, ssid_str_buffer);
    EEPROM.put(PWD_OFFSET, pwd_str_buffer);
    return EEPROM.commit();
}

int Settings::get_sensor_id() {
    return SENSOR_ID;
}

const char *Settings::get_sensor_key() {
    return SENSOR_KEY;
}

const char *Settings::get_sensor_id_str() {
    if (*id_str_buffer == 0) {
        iota(get_sensor_id(), id_str_buffer, sizeof(id_str_buffer));
    }
    return id_str_buffer;
}

const char *Settings::get_wifi_ssid() {
    unsigned long canary;
    EEPROM.get(WIFI_CANARY_OFFSET, canary);
    if (canary == CANARY) {
        if (*ssid_str_buffer == 0) {
            EEPROM.get(SSID_OFFSET, ssid_str_buffer);
        }
        return ssid_str_buffer;
    }
    return emptyString.c_str();
}
const char *Settings::get_wifi_pwd() {
    unsigned long canary;
    EEPROM.get(WIFI_CANARY_OFFSET, canary);
    if (canary == CANARY) {
        if (*pwd_str_buffer == 0) {
            EEPROM.get(PWD_OFFSET, pwd_str_buffer);
        }
        return pwd_str_buffer;
    }
    return emptyString.c_str();
}