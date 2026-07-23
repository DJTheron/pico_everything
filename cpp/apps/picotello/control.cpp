#include "control.h"

#include <cstdlib>

#include "lib/input.h"

namespace control {
namespace {

constexpr int SPEED   = 40;  // bang-bang stick magnitude for the digital joystick
constexpr int FPV_SAG = 30;  // rest-throttle sink in FPV mode
constexpr int FPV_K   = 40;  // bank-to-altitude coupling (per 100 of tilt)

int clamp100(int v) { return v < -100 ? -100 : (v > 100 ? 100 : v); }

}  // namespace

const char* mode_name(Mode m) { return m == Mode::FPV ? "FPV" : "CAMERA"; }

Sticks read_joystick() {
    Sticks s{0, 0, 0, 0};
    bool shift = input::held(input::CTRL);
    bool up = input::held(input::UP),   dn = input::held(input::DOWN);
    bool lf = input::held(input::LEFT), rt = input::held(input::RIGHT);
    if (!shift) {                       // pitch / roll
        s.fb = up ? SPEED : (dn ? -SPEED : 0);
        s.lr = rt ? SPEED : (lf ? -SPEED : 0);
    } else {                           // throttle / yaw
        s.ud  = up ? SPEED : (dn ? -SPEED : 0);
        s.yaw = rt ? SPEED : (lf ? -SPEED : 0);
    }
    return s;
}

Sticks mix(Sticks in, Mode mode) {
    Sticks out = in;
    if (mode == Mode::FPV) {
        int tilt = abs(in.fb) + abs(in.lr);
        out.ud = clamp100(in.ud - FPV_SAG - (FPV_K * tilt) / 100);
    }
    return out;
}

}  // namespace control
