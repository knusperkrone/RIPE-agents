#include "server.h"

AsyncWebServer server(80);
unsigned long start_time;
void (*connect_callback_ptr)(const char *, const char *);
void (*teardown_callback_ptr)();

AsyncCallbackJsonWebHandler request_handler("/config/wifi", [](AsyncWebServerRequest *request, JsonVariant &json) {
    const JsonObject &jsonObj = json.as<JsonObject>();
    const char *ssid = jsonObj["ssid"];
    const char *pwd = jsonObj["pwd"];
    if (ssid && pwd) {
        connect_callback_ptr(ssid, pwd);
        request->send(200);
    } else {
        request->send(403);
    }
});

void ConfigServer::start(void (*connect_callback)(const char *, const char *), void (*teardown_callback)()) {
    if (start_time != 0) {
        return;
    }

    connect_callback_ptr = connect_callback;
    teardown_callback_ptr = teardown_callback;

    server.addHandler(&request_handler).setFilter(ON_AP_FILTER);
    server.begin();
    start_time = millis();

    Serial.print("[INFO] Started Webserver");
}

void ConfigServer::loop() {
    if (start_time == 0) {
        return;
    }
    auto up_delta = millis() - start_time;
    if (up_delta > CONFIG_SERVER_UPTIME) {
        ConfigServer::end();
    } else {
        int up_secs = (CONFIG_SERVER_UPTIME - up_delta) / 1000;
        Serial.print("[INFO] Webserver is online for secs: ");
        Serial.println(up_secs);
    }
}

void ConfigServer::end() {
    // server.end();
    // server.removeHandler(&request_handler);
    teardown_callback_ptr();
    start_time = 0;
    Serial.print("[INFO] Ended Webserver");
}
