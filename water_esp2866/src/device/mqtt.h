#pragma once

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include "constants.h"
#include "settings.h"
#include "utils.h"

void mqtt_setup(MQTT_CALLBACK_SIGNATURE);
void mqtt_loop();
void mqtt_send(char *topic, char *payload);

extern WiFiClient wifiClient;
