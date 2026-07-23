#include "hud.h"

#include <cstdio>

#include "lib/colors.h"

namespace hud {
namespace {

uint16_t battery_color(int pct) {
    if (pct > 50) return color::GREEN;
    if (pct > 20) return color::YELLOW;
    return color::RED;
}

uint16_t link_color(Link l) {
    switch (l) {
        case Link::OK:    return color::GREEN;
        case Link::STALE: return color::YELLOW;
        default:          return color::RED;
    }
}

}  // namespace

void draw(Canvas& c, const tello::Telemetry& t, bool flying,
          const char* mode, Link link, const control::Sticks& cmd) {
    char buf[40];
    c.fill(color::BLACK);

    // Top: mode label + link dot. No big title.
    c.text(mode, 6, 6, color::CYAN, 2);
    c.circle(228, 14, 7, link_color(link), true);

    // Battery: big number + bar.
    c.text("BATTERY", 6, 30, color::WHITE, 1);
    snprintf(buf, sizeof(buf), "%d%%", t.bat);
    c.text(buf, 6, 42, battery_color(t.bat), 3);
    int bx = 110, by = 46, bw = 122, bh = 20;
    c.rect(bx, by, bw, bh, color::WHITE);
    int fillw = (t.bat * (bw - 4)) / 100;
    if (fillw < 0) fillw = 0;
    if (fillw > bw - 4) fillw = bw - 4;
    c.fill_rect(bx + 2, by + 2, fillw, bh - 4, battery_color(t.bat));

    // Altitude: big.
    c.text("ALTITUDE", 6, 80, color::WHITE, 1);
    snprintf(buf, sizeof(buf), "%dcm", t.h);
    c.text(buf, 6, 92, color::WHITE, 3);

    // Attitude / ToF, small.
    snprintf(buf, sizeof(buf), "TOF %d  P%d R%d Y%d", t.tof, t.pitch, t.roll, t.yaw);
    c.text(buf, 6, 126, color::GREY, 1);

    // Commanded rc (what we're sending the drone) — useful props-off.
    snprintf(buf, sizeof(buf), "RC L%d F%d U%d Y%d", cmd.lr, cmd.fb, cmd.ud, cmd.yaw);
    c.text(buf, 6, 140, color::CYAN, 1);

    // Flying / landed banner.
    if (flying) {
        c.fill_rect(6, 158, 228, 24, color::RED);
        c.text("FLYING", 72, 162, color::WHITE, 2);
    } else {
        c.rect(6, 158, 228, 24, color::GREEN);
        c.text("LANDED", 72, 162, color::GREEN, 2);
    }

    // Link status + last drone reply (bottom two lines). The action line at
    // y=190 is drawn by the caller.
    if (link == Link::DISCONNECTED)
        c.text("!! DISCONNECTED", 6, 208, color::RED, 1);
    else if (link == Link::STALE)
        c.text("! no telemetry", 6, 208, color::YELLOW, 1);

    const char* r = tello::last_response();
    if (r[0]) {
        snprintf(buf, sizeof(buf), "TELLO: %s", r);
        c.text(buf, 6, 222, color::GREY, 1);
    }
}

}  // namespace hud
