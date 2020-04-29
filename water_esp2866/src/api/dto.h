#pragma once

#include <ArduinoJson.h>

#include "constants.h"

#define REGISTER_PAYLOAD "{ \"name\": \"" SENSOR_NAME "\", \"agents\": [ { \"domain\": \"" SENSOR_DOMAIN "\", \"agent_name\": \"" SENSOR_AGENT "\" } ] }"

// https://arduinojson.org/v6/assistant/
extern StaticJsonDocument<25> registerRespBuffer;
extern StaticJsonDocument<75> cmdMsgBuffer;
