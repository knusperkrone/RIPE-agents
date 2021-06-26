#pragma once

class OfflineAgent {
    static long last_watered;
    static bool active;

   public:
    static void setup();
    static void loop();
    static void stop();
};