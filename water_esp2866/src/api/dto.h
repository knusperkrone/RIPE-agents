#pragma once

#include <ArduinoJson.h>

#include "constants.h"

// https://arduinojson.org/v6/assistant/
extern StaticJsonDocument<48> registerRespBuffer;
extern StaticJsonDocument<75> cmdMsgBuffer;
