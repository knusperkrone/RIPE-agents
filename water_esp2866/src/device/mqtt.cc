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
    if (!mqttClient.connected()) {
        Mqtt::reconnect();
    }
    mqttClient.publish(topic, payload);
}

void Mqtt::reconnect() {
    if (!mqttClient.connected()) {
        // Concat sensor name
        const char *sensor_id = settings.get_sensor_id_str();
        int prefix_len = strlen(MQTT_NAME_PREFIX);
        int id_len = strlen(sensor_id);

        char name[prefix_len + id_len + 1];
        char *nameBase = name;
        memccpy(nameBase, MQTT_NAME_PREFIX, '\0', prefix_len);
        nameBase += prefix_len;
        memccpy(nameBase, sensor_id, '\0', id_len);
        nameBase += id_len;
        *nameBase = '\0';

        while (!mqttClient.connected()) {
            Serial.println("[INFO] Reconnecting MQTT...");
            if (!mqttClient.connect(name)) {
                Serial.print("[ERROR] failed, rc=");
                Serial.print(mqttClient.state());
                Serial.println(" retrying in 3 seconds");
                delay(3000);
            }
        }

        // Concat CMD topic
        char cmdTopic[strlen(MQTT_CMD_PATH) + strlen(sensor_id) + 1];
        concat(cmdTopic, MQTT_CMD_PATH, sensor_id);

        mqttClient.subscribe(cmdTopic);
    }
}
