#include "backend.h"

int BackendAdapter::setup() {
    Serial.println("[INFO] Registering to backend");
    int sensor_id = settings.get_sensor_id();
    if (sensor_id < 0) {
        sensor_id = BackendAdapter::fetch_sensor_id();
        if (sensor_id < 0) {
            delay(100);
            Wifi::reconnect();
            return BackendAdapter::setup();  // Recurse or die!
        } else {
            settings.set_sensor_id(sensor_id);
        }
        Serial.print("[DEBUG] Fetched id ");
    } else {
        Serial.print("[INFO] Using cached id ");
    }
    Serial.println(sensor_id);

    return sensor_id;
}

void BackendAdapter::send_data() {
    static unsigned long last_send;

    if (millis() - last_send > SEND_TIMEOUT_MS) {
        last_send = millis();
        int moisture = Sensor::read_moisture();

        const char *sensor_id = settings.get_sensor_id_str();
        char cmdTopic[strlen(MQTT_DATA_PATH) + strlen(sensor_id) + 1];
        concat(cmdTopic, MQTT_DATA_PATH, sensor_id);

        char buffer[256];
        StaticJsonDocument<256> doc;
        doc["moisture"] = moisture;
        serializeJson(doc, buffer);

        Serial.print("[INFO] Sending moisture: ");
        Serial.println(moisture);
        Mqtt::send(cmdTopic, buffer);
    }
}

int BackendAdapter::fetch_sensor_id() {
    Serial.println("[INFO] Fetching sensor_id from backend");

    HTTPClient httpClient;
    httpClient.begin(wifiClient, BACKEND_URL BACKEND_SENSOR_PATH);
    httpClient.addHeader("Content-Type", "application/json");

    int fetched_id = -1;
    int code = httpClient.POST(REGISTER_PAYLOAD);
    if (code > 0) {
        if (code == 200) {
            String msg = httpClient.getString();

            DeserializationError error = deserializeJson(registerRespBuffer, msg);
            if (error) {
                Serial.println("[ERROR] Failed to deserialize backend response");
            } else {
                fetched_id = registerRespBuffer["id"];
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

    return fetched_id;
}
