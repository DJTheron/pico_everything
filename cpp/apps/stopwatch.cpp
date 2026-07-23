// Stopwatch — port of apps/Clock/Stopwatch.py.
#include <cstdio>

#include "pico/stdlib.h"

#include "lib/canvas.h"
#include "lib/colors.h"
#include "lib/input.h"

extern Canvas g_canvas;

namespace {

void display_time(uint32_t ms_passed) {
    uint32_t hours   = ms_passed / 3600000u;
    uint32_t minutes = (ms_passed % 3600000u) / 60000u;
    uint32_t seconds = (ms_passed % 60000u) / 1000u;
    uint32_t ms      = ms_passed % 1000u;

    char buf[16];
    snprintf(buf, sizeof(buf), "%02lu:%02lu:%02lu.%03lu",
             (unsigned long)hours, (unsigned long)minutes,
             (unsigned long)seconds, (unsigned long)ms);

    g_canvas.fill(color::BLACK);
    g_canvas.text("Stopwatch", 48, 40, color::GREEN, 2);
    g_canvas.text(buf, 24, 112, color::WHITE, 2);
    g_canvas.show();
}

uint32_t now_ms() { return to_ms_since_boot(get_absolute_time()); }

// The running/paused loop. Returns to the app's idle screen on Y.
void run_stopwatch() {
    bool running = true;
    uint32_t offset = 0;
    uint32_t start = now_ms();
    uint32_t ms_passed = 0;

    while (true) {
        input::update();
        if (running) ms_passed = (now_ms() - start) + offset;
        display_time(ms_passed);

        if (input::pressed(input::Y)) return;

        if (input::pressed(input::A)) {
            if (running) {
                offset = ms_passed;   // freeze accumulated time
                running = false;
            } else {
                start = now_ms();      // resume from the frozen offset
                running = true;
            }
        }
        sleep_ms(1);
    }
}

}  // namespace

void stopwatch_run() {
    display_time(0);
    while (true) {
        input::update();
        if (input::pressed(input::A)) {
            run_stopwatch();
            display_time(0);
        }
        if (input::pressed(input::Y)) return;
        sleep_ms(10);
    }
}
