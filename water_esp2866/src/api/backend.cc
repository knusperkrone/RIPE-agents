#include "backend.h"

std::tuple<int, char *> BackendAdapter::setup() {
    Serial.println("[INFO] Registering to backend");
    int sensor_id = settings.get_sensor_id();
    char *sensor_key = settings.get_sensor_key();
    if (sensor_id < 0) {
        std::tie(sensor_id, sensor_key) = BackendAdapter::register_sensor();
        if (sensor_id < 0) {
            delay(250);
            Wifi::reconnect();
            return BackendAdapter::setup();  // Recurse or die!
        } else {
            settings.set_sensor_data(sensor_id, sensor_key);
        }
        Serial.print("[DEBUG] fetched key ");
        Serial.println(sensor_key);
        Serial.print("[DEBUG] Fetched id ");
    } else {
        Serial.print("[INFO] Using cached id ");
    }
    Serial.println(sensor_id);

    return std::tuple<int, char *>{0, sensor_key};
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

std::tuple<int, char *> BackendAdapter::register_sensor() {
    Serial.println("[INFO] Fetching sensor_id from backend");

    HTTPClient httpClient;
    httpClient.begin(wifiClient, BACKEND_URL BACKEND_SENSOR_PATH);
    httpClient.addHeader("Content-Type", "application/json");

    int fetched_id = -1;
    char *fetched_key = NULL;
    int code = httpClient.POST(REGISTER_PAYLOAD);
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
