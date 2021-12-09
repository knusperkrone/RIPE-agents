#pragma once
#include <stdint.h>

struct AgentConfig {
    const char* domain;
    const char* agent;
    void (*callback)(int32_t);
};

// MQTT BROKER SETTINGS
#define MQTT_NAME_PREFIX "WaterSensor_"

// BACKEND SETTINGS
//#define BACKEND_URL "http://192.168.1.57:8000"
#define BACKEND_URL "http://retroapp.if-lab.de:8000"
// BACKEND CONSTATNS
#define BACKEND_SENSOR_PATH "/api/sensor"
#define MQTT_DATA_PATH "sensor/data/"
#define MQTT_CMD_PATH "sensor/cmd/"

// SENSOR CONFIG
#define SEND_TIMEOUT_MS 30 * 1000
#define SENSOR_NAME "REFERENCE_SENSOR"
#define WATER_RELAY D8
#define MOISTURE_SENSOR A0
extern const AgentConfig AGENTS[1];

// WLAN NETWORK
#define WLAN_SSID "InterFace-Bewässerung"
#define CONFIG_SERVER_UPTIME 8 * 60 * 1000