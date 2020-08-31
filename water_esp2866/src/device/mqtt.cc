#include "mqtt.h"

PubSubClient mqttClient(wifiClient);

void Mqtt::setup(MQTT_CALLBACK_SIGNATURE) {
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(callback);
}

void Mqtt::loop() {
    if (!mqttClient.connected()) {
        Mqtt::reconnect();
    }
    mqttClient.loop();
}

void Mqtt::send(char *topic, char *payload) {
    mqttClient.loop();
    if (!mqttClient.connected()) {
        Mqtt::reconnect();
    }
    mqttClient.publish(topic, payload);
}

void Mqtt::reconnect() {
    if (!mqttClient.connected()) {
        // Concat sensor name
        const char *sensor_id = settings.get_sensor_id_str();
        const char *sensor_key = settings.get_sensor_key();
        int prefix_len = strlen(MQTT_NAME_PREFIX);
        int id_len = strlen(sensor_id);

        char sensor_name[prefix_len + id_len + 1];
        concat(sensor_name, 2, MQTT_NAME_PREFIX, sensor_id);

        while (!mqttClient.connected()) {
            Serial.print("[INFO] Reconnecting MQTT as ");
            Serial.println(sensor_name);
            if (!mqttClient.connect(sensor_name)) {
                Serial.print("[ERROR] failed, rc=");
                Serial.print(mqttClient.state());
                Serial.println(" retrying in 3 seconds");
                delay(3000);
            }
        }

        // Concat CMD topic
        char cmdTopic[strlen(MQTT_CMD_PATH) + strlen(sensor_id) + 1];
        concat(cmdTopic, 4, MQTT_CMD_PATH, sensor_id, "/", sensor_key);

        mqttClient.subscribe(cmdTopic);
        Serial.println("[INFO] Connected MQTT");
    }
}
