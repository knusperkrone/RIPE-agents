#pragma once

#include <ArduinoJson.h>

#include "constants.h"

// https://arduinojson.org/v6/assistant/
extern StaticJsonDocument<256> cmdMsgBuffer;
extern StaticJsonDocument<2048> brokerBuffer;
