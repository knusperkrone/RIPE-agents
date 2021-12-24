#include "backend.h"

String *BackendAdapter::commandTopic;

bool BackendAdapter::setup(int tries) {
    const char *sensorId = settings.get_sensor_id_str();
    const char *sensorKey = settings.get_sensor_key();

    // Build command topic
    char cmdTopic[strlen(MQTT_DATA_PATH) + strlen(sensorId) + 1 + strlen(sensorKey) + 1];
    concat(cmdTopic, 4, MQTT_DATA_PATH, sensorId, "/", sensorKey);
    BackendAdapter::commandTopic = new String(cmdTopic);

    Serial.print("[INFO] Sensor id: ");
    Serial.println(sensorId);
    Serial.print("[INFO] Sensor key: ");
    Serial.println(sensorKey);
    Serial.print("[INFO] Command topic: ");
    Serial.println(BackendAdapter::commandTopic->c_str());

    return true;
}

std::tuple<const char *, int> BackendAdapter::fetch_mqtt_broker() {
    const char *sensorId = settings.get_sensor_id_str();
    const char *sensorKey = settings.get_sensor_key();

    // Build command topic
    char url_buffer[strlen(BACKEND_URL BACKEND_SENSOR_PATH "/") + strlen(sensorId) + 1];
    concat(url_buffer, 2, BACKEND_URL BACKEND_SENSOR_PATH "/", sensorId);

    HTTPClient httpClient;
    httpClient.begin(wifiClient, url_buffer);
    httpClient.addHeader("Content-Type", "application/json");
    httpClient.addHeader("X-Key", sensorKey);

    char *brokerField = NULL;
    int code = httpClient.GET();
    if (code > 0) {
        if (code == 200) {
            String msg = httpClient.getString();
            DeserializationError error = deserializeJson(brokerBuffer, msg);
            if (error) {
                Serial.println("[ERROR] Failed to deserialize backend response");
                Serial.println(error.c_str());
            } else {
                brokerField = (char *)((const char *)brokerBuffer["broker"]);
            }
        } else {
            Serial.print("[ERROR] Invalid backend response: ");
            Serial.println(code);
        }
    } else {
        Serial.print("[ERROR] Http error: ");
        Serial.println(httpClient.errorToString(code));
        httpClient.end();
        return std::make_tuple(brokerField, -1);
    }
    httpClient.end();

    // split tcp://BROKER_IP:BROKER_PORT
    Serial.print("[INFO] Broker ");
    Serial.println(brokerField);

    brokerField += strlen("tcp://");
    char *broker = strtok(brokerField, ":");
    char *port = strtok(NULL, ":");
    return std::make_tuple(broker, std::stoi(port));
}

void BackendAdapter::send_sensor_data() {
    static unsigned long last_send_ms;
    unsigned long curr_ms = millis();

    if (curr_ms - last_send_ms > SEND_TIMEOUT_MS) {
        last_send_ms = curr_ms;

        // Get sensor data
        int moisture = Sensor::read_moisture();

        char buffer[256];
        StaticJsonDocument<256> doc;
        doc["moisture"] = moisture;
        serializeJson(doc, buffer);

        Serial.print("[INFO] Sending moisture: ");
        Serial.println(moisture);
        Mqtt::send((char *)BackendAdapter::commandTopic->c_str(), buffer);
    }
}