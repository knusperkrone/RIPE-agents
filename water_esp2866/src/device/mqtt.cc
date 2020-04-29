#include "mqtt.h"

PubSubClient mqttClient(wifiClient);

void mqtt_setup(MQTT_CALLBACK_SIGNATURE) {
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(callback);
}

void mqtt_reconnect() {
    if (!mqttClient.connected()) {
        // Concat sensor name
        int prefix_len = strlen(MQTT_NAME_PREFIX);
        int id_len = strlen(get_sensor_id_str());

        char name[prefix_len + id_len + 1];
        char *nameBase = name;
        memccpy(nameBase, MQTT_NAME_PREFIX, '\0', prefix_len);
        nameBase += prefix_len;
        memccpy(nameBase, get_sensor_id_str(), '\0', id_len);
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
    }

    // Concat CMD topic
    const char *sensor_id = get_sensor_id_str();
    char cmdTopic[strlen(MQTT_CMD_PATH) + strlen(sensor_id) + 1];
    concat(cmdTopic, MQTT_CMD_PATH, sensor_id);

    mqttClient.subscribe(cmdTopic);
}

void mqtt_loop() {
    if (!mqttClient.connected()) {
        mqtt_reconnect();
    }
    mqttClient.loop();
}

void mqtt_send(char *topic, char *payload) {
    if (!mqttClient.connected()) {
        mqtt_reconnect();
    }
    mqttClient.publish(topic, payload);
}