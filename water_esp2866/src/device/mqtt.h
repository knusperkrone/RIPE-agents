#pragma once

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include "constants.h"
#include "mqtt.h"
#include "settings.h"
#include "utils.h"
#include "wifi.h"

class Mqtt {
   public:
    static void setup(MQTT_CALLBACK_SIGNATURE);
    static void loop();
    static void send(char *topic, char *payload);

   private:
    static void reconnect();
};
