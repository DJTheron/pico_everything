// Picotello — screen state machine: scan -> pick network -> connect -> fly.
// Phase 2 telemetry/takeoff/land + Phase 3 joystick flight control.
#include <cstdio>
#include <cstring>

#include "pico/stdlib.h"

#include "lib/canvas.h"
#include "lib/colors.h"
#include "lib/input.h"
#include "lib/wifi.h"
#include "control.h"
#include "hud.h"
#include "tello.h"

extern Canvas g_canvas;

namespace {

constexpr int MAX_NETS = 8;
const char* const TELLO_PREFIXES[] = {"TELLO-", "RMTT-"};

uint32_t now_ms() { return to_ms_since_boot(get_absolute_time()); }

// A centred banner over the current frame — used before blocking actions
// (takeoff/land) so the screen isn't frozen-silent while we wait.
void banner(const char* msg, uint16_t c) {
    int w = (int)strlen(msg) * 8;
    int bw = w + 24, bh = 34;
    int bx = (Canvas::W - bw) / 2, by = 100;
    g_canvas.fill_rect(bx, by, bw, bh, color::BLACK);
    g_canvas.rect(bx, by, bw, bh, c);
    g_canvas.text(msg, (Canvas::W - w) / 2, by + 13, c, 1);
    g_canvas.show();
}

// Progress bar for a press-and-hold action (fills over 1000 ms).
void hold_progress(uint32_t held, uint16_t c) {
    uint32_t p = held > 1000 ? 1000 : held;
    g_canvas.rect(6, 202, 228, 5, c);
    g_canvas.fill_rect(6, 202, (int)(p * 228 / 1000), 5, c);
}

// One-line status screen for the scan/connect steps.
void status_screen(const char* line1, const char* line2, uint16_t c) {
    g_canvas.fill(color::BLACK);
    g_canvas.text("PICOTELLO", 30, 40, color::CYAN, 2);
    g_canvas.text(line1, 20, 110, c, 1);
    if (line2) g_canvas.text(line2, 20, 130, color::GREY, 1);
    g_canvas.show();
}

// Wait (drawing a message) until Y is pressed. Used on error screens.
void wait_for_back() {
    while (true) {
        input::update();
        if (input::pressed(input::Y)) return;
        sleep_ms(30);
    }
}

// Pairing list: left/right move, A connect, Y back. Returns index or -1.
int pick_network(const wifi::Network* nets, int count) {
    int sel = 0;
    while (true) {
        input::update();
        g_canvas.fill(color::BLACK);
        g_canvas.text("Select Tello", 20, 10, color::CYAN, 2);
        for (int i = 0; i < count; ++i) {
            uint16_t c = (i == sel) ? color::GREEN : color::WHITE;
            char row[40];
            snprintf(row, sizeof(row), "%s %s (%d)",
                     (i == sel) ? ">" : " ", nets[i].ssid, nets[i].rssi);
            g_canvas.text(row, 12, 44 + i * 20, c, 1);
        }
        g_canvas.text("A connect   Y back", 12, 214, color::GREY, 1);
        g_canvas.show();

        if (input::pressed(input::LEFT))  sel = (sel + 1) % count;
        if (input::pressed(input::RIGHT)) sel = (sel - 1 + count) % count;
        if (input::pressed(input::A))     return sel;
        if (input::pressed(input::Y))     return -1;
        sleep_ms(20);
    }
}

// The live flight screen. Returns (to the pairing flow) only via a deliberate
// Y-hold, and only once the drone is on the ground.
void fly() {
    enum State { GROUNDED, FLYING, LANDING } state = GROUNDED;
    control::Mode mode = control::Mode::CAMERA;
    control::Sticks cmd{0, 0, 0, 0};
    uint32_t x_hold = 0, y_hold = 0, landing_start = 0, exit_start = 0;
    bool exiting = false;

    while (true) {
        input::update();
        uint32_t now = now_ms();
        const tello::Telemetry& t = tello::telemetry();

        hud::Link link;
        bool wifi_up = wifi::link_up();
        if (!wifi_up)                     link = hud::Link::DISCONNECTED;
        else if (tello::link_fresh(2000)) link = hud::Link::OK;
        else                              link = hud::Link::STALE;

        // Emergency motor cutoff: hold X ~1s (the drone DROPS).
        if (input::held(input::X)) {
            if (x_hold == 0) x_hold = now;
            if (now - x_hold >= 1000) {
                tello::emergency();
                state = GROUNDED;
                exiting = false;
                x_hold = 0;
                banner("MOTORS OFF", color::RED);
                sleep_ms(700);
            }
        } else {
            x_hold = 0;
        }

        // Exit: hold Y ~1s. If airborne, land first; leave only once grounded.
        if (input::held(input::Y)) {
            if (y_hold == 0) y_hold = now;
            if (now - y_hold >= 1000) {
                if (state == GROUNDED) return;
                if (!exiting) { exiting = true; exit_start = now; }
                if (state != LANDING) {
                    tello::land();
                    state = LANDING;
                    landing_start = now;
                }
            }
        } else {
            y_hold = 0;
        }

        // Takeoff (blocks briefly until height confirms lift-off).
        if (input::pressed(input::A) && state == GROUNDED) {
            banner("TAKING OFF...", color::WHITE);
            if (tello::takeoff()) state = FLYING;
            else { banner("TAKEOFF FAILED", color::RED); sleep_ms(1000); }
        }

        // B: land while flying, or toggle flight mode while grounded.
        if (input::pressed(input::B)) {
            if (state == FLYING) {
                banner("LANDING...", color::WHITE);
                tello::land();
                state = LANDING;
                landing_start = now_ms();
            } else if (state == GROUNDED) {
                mode = (mode == control::Mode::CAMERA) ? control::Mode::FPV
                                                       : control::Mode::CAMERA;
            }
        }

        // Flight control: continuous rc while flying. This IS the keepalive too
        // (centred sticks send rc 0 0 0 0 = hover).
        if (state == FLYING) {
            cmd = control::mix(control::read_joystick(), mode);
            tello::send_rc(cmd.lr, cmd.fb, cmd.ud, cmd.yaw);
        } else {
            cmd = control::Sticks{0, 0, 0, 0};
        }

        // Landing: hands off — never re-send `land` (that restarts the descent
        // and it never touches down). Just wait for grounding or a timeout.
        if (state == LANDING) {
            if ((t.valid && t.h <= 5) || (now - landing_start > 12000)) {
                state = GROUNDED;
                if (exiting) return;
            }
        }
        // Exit even if grounding can't be confirmed (link lost / too long); the
        // drone's own 15s failsafe lands it. Never trap the user in the app.
        if (exiting && (!wifi_up || (now - exit_start) > 12000)) return;

        // ---- Draw ----
        hud::draw(g_canvas, t, state != GROUNDED, control::mode_name(mode), link, cmd);

        // App-owned action/status line at y=190 (mutually exclusive → never
        // overlaps the HUD's lines below it).
        if (state == LANDING) {
            g_canvas.text(exiting ? "LANDING, THEN EXIT" : "LANDING...",
                          6, 190, color::CYAN, 1);
        } else if (x_hold != 0) {
            g_canvas.text("HOLD X = STOP", 6, 190, color::RED, 1);
            hold_progress(now - x_hold, color::RED);
        } else if (y_hold != 0) {
            g_canvas.text("HOLD Y = EXIT", 6, 190, color::YELLOW, 1);
            hold_progress(now - y_hold, color::YELLOW);
        } else if (state == GROUNDED) {
            g_canvas.text("A takeoff  B mode  Y=exit", 6, 190, color::GREY, 1);
        } else {
            g_canvas.text("joy=fly B land Xstop Yexit", 6, 190, color::GREY, 1);
        }
        g_canvas.show();
        sleep_ms(40);   // ~25 Hz (also the rc rate while flying)
    }
}

}  // namespace

void picotello_run() {
    // Clean slate so every run behaves like a fresh boot — frees leftover
    // sockets and drops the old WiFi association (fixes reconnect failures).
    tello::end();
    wifi::disconnect();
    sleep_ms(200);

    // 1) Scan.
    status_screen("Scanning for Tello...", nullptr, color::WHITE);
    wifi::Network nets[MAX_NETS];
    int n = wifi::scan(nets, MAX_NETS, TELLO_PREFIXES, 2);
    if (n == 0) {
        status_screen("No Tello found.", "Power drone, retry. Y=back", color::RED);
        wait_for_back();
        return;
    }

    // 2) Pick.
    int idx = pick_network(nets, n);
    if (idx < 0) return;

    // 3) Connect.
    status_screen("Connecting...", nets[idx].ssid, color::WHITE);
    if (!wifi::connect_open(nets[idx].ssid, 20000)) {
        status_screen("Connect failed.", "Y = back", color::RED);
        wait_for_back();
        return;
    }

    // 4) UDP + SDK mode.
    status_screen("Entering SDK mode...", nets[idx].ssid, color::WHITE);
    if (!tello::begin() || !tello::enter_sdk_mode(8000)) {
        status_screen("SDK handshake failed.", "Y = back", color::RED);
        wait_for_back();
        return;
    }

    // 5) Fly.
    fly();
}
