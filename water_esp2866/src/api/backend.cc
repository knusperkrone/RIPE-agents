#include "backend.h"

int fetch_sensor_id() {
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

int backend_register() {
    Serial.println("[INFO] Registering to backend");
    int sensor_id = get_sensor_id();
    if (sensor_id < 0) {
        sensor_id = fetch_sensor_id();
        if (sensor_id < 0) {
            delay(100);
            return backend_register();  // Recurse or die!
        } else {
            set_sensor_id(sensor_id);
        }
        Serial.print("[DEBUG] Fetched id ");
    } else {
        Serial.print("[INFO] Using cached id ");
    }
    Serial.println(sensor_id);

    return sensor_id;
}

void send_moisture() {
    static unsigned long last_send;

    if (millis() - last_send > SEND_TIMEOUT_MS) {
        last_send = millis();
        int moisture = read_moisture();

        char cmdTopic[strlen(MQTT_DATA_PATH) + strlen(get_sensor_id_str()) + 1];
        concat(cmdTopic, MQTT_DATA_PATH, get_sensor_id_str());

        char buffer[256];
        StaticJsonDocument<256> doc;
        doc["moisture"] = moisture;
        serializeJson(doc, buffer);

        Serial.print("[INFO] Sending moisture: ");
        Serial.println(moisture);
        mqtt_send(cmdTopic, buffer);
    }
}