#include "backend.h"

bool BackendAdapter::setup(int tries) {
    int sensor_id = settings.get_sensor_id();
    const char *sensor_key = settings.get_sensor_key();

    // Check if id is valid
    if (sensor_id < 0) {
        std::tie(sensor_id, sensor_key) = BackendAdapter::register_sensor();
        if (sensor_id < 0) {
            if (tries-- == 0) {
                return false;
            }
            delay(250);
            Wifi::reconnect();
            return BackendAdapter::setup(tries);  // Recurse or die
        } else {
            // Register agents
            for (size_t i = 0; i < sizeof(AGENTS) / sizeof(AGENTS[0]); i++) {
                auto config = AGENTS[i];
                while (!BackendAdapter::register_agent(sensor_id, sensor_key, config.domain, config.agent)) {
                    if (tries-- == 0) {
                        return false;
                    }
                    delay(250);
                }
            }
            settings.set_sensor_config(sensor_id, sensor_key);
        }
    } else {
        Serial.println("[INFO] Using local settings");
    }

    Serial.print("[INFO] Sensor id: ");
    Serial.println(sensor_id);
    Serial.print("[INFO] Sensor key: ");
    Serial.println(sensor_key);
    return true;
}

void BackendAdapter::send_data() {
    static unsigned long last_send;

    if (millis() - last_send > SEND_TIMEOUT_MS) {
        last_send = millis();
        int moisture = Sensor::read_moisture();

        const char *sensor_id = settings.get_sensor_id_str();
        const char *sensor_key = settings.get_sensor_key();
        char cmdTopic[strlen(MQTT_DATA_PATH) + strlen(sensor_id) + 1 + strlen(sensor_key) + 1];
        concat(cmdTopic, 4, MQTT_DATA_PATH, sensor_id, "/", sensor_key);

        char buffer[256];
        StaticJsonDocument<256> doc;
        doc["moisture"] = moisture;
        serializeJson(doc, buffer);

        Serial.print("[INFO] Sending moisture: ");
        Serial.println(moisture);
        Mqtt::send(cmdTopic, buffer);
    }
}

std::tuple<int, const char *> BackendAdapter::register_sensor() {
    Serial.println("[INFO] Fetching sensor_id from backend");
    int fetched_id = -1;
    char *fetched_key = NULL;

    // Serialize payload
    char body_buffer[512];
    StaticJsonDocument<512> doc;
    doc[SENSOR_REGISTER_DTO_NAME] = SENSOR_NAME;
    size_t written = serializeJson(doc, body_buffer);
    if (written == 0 || written >= sizeof(body_buffer)) {
        Serial.print("[ERROR] Failed serializing agent body");
        return std::make_tuple(fetched_id, fetched_key);
    }

    // Dispatch request
    HTTPClient httpClient;
    httpClient.begin(wifiClient, BACKEND_URL BACKEND_SENSOR_PATH);
    httpClient.addHeader("Content-Type", "application/json");

    int code = httpClient.POST(body_buffer);
    if (code > 0) {
        if (code == 200) {
            String msg = httpClient.getString();
            DeserializationError error = deserializeJson(registerRespBuffer, msg);
            if (error) {
                Serial.println("[ERROR] Failed to deserialize backend response");
                Serial.println(error.c_str());
            } else {
                fetched_id = registerRespBuffer["id"];
                fetched_key = (char *)((const char *)registerRespBuffer["key"]);
            }
        } else {
            Serial.print("[ERROR] Invalid backend response: ");
            Serial.println(code);
        }
    } else {
        Serial.print("[ERROR] Http error: ");
        Serial.println(httpClient.errorToString(code));
    }
    httpClient.end();

    return std::make_tuple(fetched_id, fetched_key);
}

bool BackendAdapter::register_agent(int id, const char *key, const char *domain, const char *agent) {
    Serial.println("[INFO] Registering agent from backend");

    // Convert id to string
    char id_buffer[12];
    iota(id, id_buffer, sizeof(id_buffer) - 1);

    // Concat url
    char url_buffer[sizeof(BACKEND_URL) + sizeof(BACKEND_AGENT_PATH) + 1 + strlen(id_buffer) + 1 + strlen(key)];
    concat(url_buffer, 4, BACKEND_URL BACKEND_AGENT_PATH "/", id_buffer, "/", key);

    // Serialize payload
    char body_buffer[512];
    StaticJsonDocument<512> doc;
    doc[AGENT_REGISTER_DTO_DOMAIN] = domain;
    doc[AGENT_REGISTER_DTO_AGENT_NAME] = agent;
    size_t written = serializeJson(doc, body_buffer);
    if (written == 0 || written >= sizeof(body_buffer)) {
        Serial.print("[ERROR] Failed serializing agent body, written bytes: ");
        Serial.println(written);
        return false;
    }

    // Dispatch request
    HTTPClient httpClient;
    httpClient.begin(wifiClient, url_buffer);
    httpClient.addHeader("Content-Type", "application/json");

    bool ret = false;
    int code = httpClient.POST(body_buffer);
    if (code > 0) {
        if (code == 200) {
            ret = true;
            Serial.print("[INFO] Registered agent ");
            Serial.print(agent);
            Serial.print(" on domain ");
            Serial.println(domain);
        } else {
            Serial.print("[ERROR] Invalid backend response: ");
            Serial.println(code);
        }
    } else {
        Serial.print("[ERROR] Http error: ");
        Serial.println(httpClient.errorToString(code));
    }
    httpClient.end();

    return ret;
}