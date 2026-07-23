#pragma once

// Flight input + mixing. The seam that lets the on-board joystick now, and the
// Xbox pad later, feed the same rc pipeline (plan's read_input() seam).
namespace control {

struct Sticks {
    int lr;   // roll   -100..100
    int fb;   // pitch  -100..100 (forward +)
    int ud;   // throttle/vertical -100..100
    int yaw;  // -100..100
};

enum class Mode { CAMERA, FPV };
const char* mode_name(Mode m);

// Read the Pico joystick into bang-bang stick values. The joystick alone drives
// pitch/roll; holding CTRL (joystick press) shifts it to throttle/yaw — so one
// 4-way stick + shift covers all four axes. (Analog Xbox sticks replace this in
// Phase 4 behind the same Sticks return.)
Sticks read_joystick();

// Apply the flight mode. CAMERA = passthrough (centre = altitude hold). FPV =
// throttle sag + bank-to-altitude coupling: rest throttle sinks and tilting
// costs altitude, so you feed throttle in during maneuvers.
Sticks mix(Sticks in, Mode mode);

}  // namespace control
