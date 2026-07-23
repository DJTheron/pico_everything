#pragma once

#include "lib/canvas.h"
#include "control.h"
#include "tello.h"

namespace hud {

enum class Link {
    OK,            // linked and telemetry is fresh
    STALE,         // linked but no recent state packet
    DISCONNECTED,  // WiFi link down (drone off / out of range)
};

// Draw the flight cockpit: battery and altitude in large type, attitude, the
// commanded rc, mode, flying/landed state and a link indicator. The bottom
// action/status line (y>=190) is left for the caller to draw so transient
// messages don't collide. Caller flushes the canvas.
void draw(Canvas& c, const tello::Telemetry& t, bool flying,
          const char* mode, Link link, const control::Sticks& cmd);

}  // namespace hud
