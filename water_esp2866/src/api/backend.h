#pragma once

#include <Arduino.h>
#include <ESP8266HTTPClient.h>

#include "device/mqtt.h"
#include "device/settings.h"
#include "device/sensors.h"
#include "dto.h"

int backend_register();
void send_moisture();

extern WiFiClient wifiClient;