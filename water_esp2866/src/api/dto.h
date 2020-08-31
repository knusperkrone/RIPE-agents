#pragma once

#include <ArduinoJson.h>

#include "constants.h"

#define REGISTER_PAYLOAD "{ \"name\": \"" SENSOR_NAME "\", \"agents\": [ { \"domain\": \"" SENSOR_WATER_DOMAIN "\", \"agent_name\": \"" SENSOR_WATER_AGENT "\" } ] }"

// https://arduinojson.org/v6/assistant/
extern StaticJsonDocument<48> registerRespBuffer;
extern StaticJsonDocument<75> cmdMsgBuffer;
