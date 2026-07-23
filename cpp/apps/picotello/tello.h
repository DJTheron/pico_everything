#pragma once
#include <cstdint>

// DJI Tello SDK 2.0 link over UDP.
//   commands -> 192.168.10.1:8889   (we send; drone replies "ok"/"error")
//   state    <- :8890               (drone pushes "key:val;..." unsolicited)
namespace tello {

struct Telemetry {
    int bat = 0;         // battery %
    int h = 0;           // height cm (relative)
    int tof = 0;         // time-of-flight height cm
    int templ = 0, temph = 0;  // temperature range
    int pitch = 0, roll = 0, yaw = 0;
    int vgx = 0, vgy = 0, vgz = 0;  // velocity
    float baro = 0.f;
    bool valid = false;          // have we ever parsed a packet
    uint32_t last_update_ms = 0; // ms-since-boot of the last packet
};

// Create the UDP sockets and bind the state listener. Call once after WiFi is
// connected. Returns false if socket setup fails.
bool begin();

// Free the UDP sockets. Call when leaving the app so a later begin() starts
// clean (otherwise the telemetry port stays bound and reconnect fails).
void end();

// Send "command" and wait up to timeout_ms for the "ok" reply. Must succeed
// before any flight command is accepted.
bool enter_sdk_mode(uint32_t timeout_ms);

// Fire-and-forget UDP command (no wait). Safe to call frequently.
void send_command(const char* cmd);

// "rc <lr> <fb> <ud> <yaw>", each clamped to [-100,100]. No reply expected.
void send_rc(int lr, int fb, int ud, int yaw);

// Discrete flight commands. takeoff/land send and wait for the drone's "ok",
// resending to survive UDP packet loss; they return false on refusal/timeout.
// emergency cuts motors immediately (fire-and-forget, sent a few times).
bool takeoff();
bool land();
void emergency();

// Latest parsed telemetry. Updated from the UDP receive callback.
const Telemetry& telemetry();

// true if a state packet arrived within `fresh_ms` of now.
bool link_fresh(uint32_t fresh_ms);

// The drone's most recent raw command reply (e.g. "ok", "error...") — for the
// on-screen diagnostic line. Empty until the first reply.
const char* last_response();

}  // namespace tello
