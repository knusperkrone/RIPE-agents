// MQTT BROKER SETTINGS
#define MQTT_BROKER "18.196.113.35"
#define MQTT_PORT 1883
#define MQTT_NAME_PREFIX "WaterSensor_"

// BACKEND SETTINGS
//#define BACKEND_URL "http://192.168.1.57:8000"
#define BACKEND_URL "http://192.168.178.47:8000"
// BACKEND CONSTATNS
#define BACKEND_SENSOR_PATH "/api/sensor"
#define BACKEND_AGENT_PATH "/api/agent"
#define MQTT_DATA_PATH "sensor/data/"
#define MQTT_CMD_PATH "sensor/cmd/"
// DTO KEYS
#define SENSOR_REGISTER_DTO_NAME "name"
#define AGENT_REGISTER_DTO_DOMAIN "domain"
#define AGENT_REGISTER_DTO_AGENT_NAME "agent_name"

// SENSOR CONFIG
#define SEND_TIMEOUT_MS 30 * 1000
#define SENSOR_NAME "REFERENCE_SENSOR"
#define SENSOR_WATER_DOMAIN "water"
#define SENSOR_WATER_AGENT "ThresholdAgent"
#define WATER_RELAY D8
#define MOISTURE_SENSOR A0

// WLAN NETWORK
#define WLAN_SSID "InterFace-Bewässerung"
#define CONFIG_SERVER_UPTIME 5 * 60 * 1000