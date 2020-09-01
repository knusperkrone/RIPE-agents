#include "settings.h"

void Settings::setup() {
    static_assert(XXX_OFFSET < 512, "Memory buffer is larger than the EEPROM");

    *key_str_buffer = 0;
    *id_str_buffer = 0;
    *ssid_str_buffer = 0;
    *pwd_str_buffer = 0;
    EEPROM.begin(512);
}

bool Settings::set_sensor_config(int id, const char *key) {
    if (strlen(key) + 1 > sizeof(key_str_buffer)) {
        Serial.println("[ERROR] cannot save sensor config");
        return false;
    }
    strcpy(key_str_buffer, key);
    EEPROM.put(SENSOR_CANARY_OFFSET, CANARY);
    EEPROM.put(ID_OFFSET, id);
    EEPROM.put(KEY_OFFSET, key_str_buffer);
    return EEPROM.commit();
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

const char *Settings::get_sensor_key() {
    unsigned long canary;
    EEPROM.get(SENSOR_CANARY_OFFSET, canary);
    if (canary == CANARY) {
        if (*key_str_buffer == 0) {
            EEPROM.get(KEY_OFFSET, key_str_buffer);
        }
        return key_str_buffer;
    }
    return emptyString.c_str();
}

int Settings::get_sensor_id() {
    unsigned long canary;
    EEPROM.get(SENSOR_CANARY_OFFSET, canary);
    if (canary == CANARY) {
        int id;
        EEPROM.get(ID_OFFSET, id);
        return id;
    }
    return -1;
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