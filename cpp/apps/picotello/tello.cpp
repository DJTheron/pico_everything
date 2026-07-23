#include "tello.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"

namespace tello {
namespace {

constexpr const char* TELLO_IP = "192.168.10.1";
constexpr uint16_t CMD_PORT   = 8889;  // we send here
constexpr uint16_t STATE_PORT = 8890;  // drone pushes here

udp_pcb* cmd_pcb = nullptr;
udp_pcb* state_pcb = nullptr;

Telemetry g_tel;              // updated in the state recv callback
volatile int g_ack = 0;       // command reply: 0=none, 1="ok", 2="error"/other
char g_last_resp[32] = "";    // raw last reply, for on-screen diagnostics

// Parse "pitch:0;roll:0;...;bat:87;...;baro:12.3;..." into g_tel.
// Runs in the lwIP callback (background IRQ) — keep it light; a HUD tolerates
// the (rare) torn read of an int field.
void parse_state(const char* s) {
    Telemetry t = g_tel;  // start from current so unlisted fields persist
    const char* p = s;
    while (*p) {
        char key[8];
        int ki = 0;
        while (*p && *p != ':' && *p != ';' && ki < 7) key[ki++] = *p++;
        key[ki] = '\0';
        if (*p != ':') { if (*p) p++; continue; }
        p++;  // skip ':'
        const char* v = p;
        while (*p && *p != ';') p++;
        int iv = atoi(v);
        if      (!strcmp(key, "bat"))   t.bat = iv;
        else if (!strcmp(key, "h"))     t.h = iv;
        else if (!strcmp(key, "tof"))   t.tof = iv;
        else if (!strcmp(key, "templ")) t.templ = iv;
        else if (!strcmp(key, "temph")) t.temph = iv;
        else if (!strcmp(key, "pitch")) t.pitch = iv;
        else if (!strcmp(key, "roll"))  t.roll = iv;
        else if (!strcmp(key, "yaw"))   t.yaw = iv;
        else if (!strcmp(key, "vgx"))   t.vgx = iv;
        else if (!strcmp(key, "vgy"))   t.vgy = iv;
        else if (!strcmp(key, "vgz"))   t.vgz = iv;
        else if (!strcmp(key, "baro"))  t.baro = (float)atof(v);
        if (*p == ';') p++;
    }
    t.valid = true;
    t.last_update_ms = to_ms_since_boot(get_absolute_time());
    g_tel = t;
}

void state_recv(void*, udp_pcb*, pbuf* p, const ip_addr_t*, u16_t) {
    if (!p) return;
    char buf[256];
    u16_t n = p->tot_len < sizeof(buf) - 1 ? p->tot_len : sizeof(buf) - 1;
    pbuf_copy_partial(p, buf, n, 0);
    buf[n] = '\0';
    parse_state(buf);
    pbuf_free(p);
}

void cmd_recv(void*, udp_pcb*, pbuf* p, const ip_addr_t*, u16_t) {
    if (!p) return;
    char buf[64];
    u16_t n = p->tot_len < sizeof(buf) - 1 ? p->tot_len : sizeof(buf) - 1;
    pbuf_copy_partial(p, buf, n, 0);
    buf[n] = '\0';
    g_ack = (strncmp(buf, "ok", 2) == 0) ? 1 : 2;
    // Keep the raw reply (trimmed) for the on-screen diagnostic line.
    int k = 0;
    while (k < 31 && buf[k] && buf[k] != '\r' && buf[k] != '\n') {
        g_last_resp[k] = buf[k];
        ++k;
    }
    g_last_resp[k] = '\0';
    pbuf_free(p);
}

void udp_send_str(udp_pcb* pcb, const char* s) {
    if (!pcb) return;
    size_t len = strlen(s);
    cyw43_arch_lwip_begin();
    pbuf* p = pbuf_alloc(PBUF_TRANSPORT, len, PBUF_RAM);
    if (p) {
        memcpy(p->payload, s, len);
        udp_send(pcb, p);
        pbuf_free(p);
    }
    cyw43_arch_lwip_end();
}

int clamp100(int v) { return v < -100 ? -100 : (v > 100 ? 100 : v); }

// Send a command and wait for the drone's "ok", resending once early to beat a
// lost first packet (WiFi is lossy — this is what fixed "had to press takeoff
// several times"). Returns true only on "ok"; false on "error" or timeout.
// Blocks up to timeout_ms, so use only for discrete actions, never in the rc
// loop. Does NOT spam the command during a multi-second maneuver.
bool send_reliable(const char* cmd, uint32_t timeout_ms) {
    g_ack = 0;
    send_command(cmd);
    bool resent = false;
    uint32_t elapsed = 0;
    while (elapsed < timeout_ms) {
        if (g_ack == 1) return true;
        if (g_ack == 2) return false;   // drone received but refused
        sleep_ms(50);
        elapsed += 50;
        if (!resent && elapsed >= 800) { send_command(cmd); resent = true; }
    }
    return g_ack == 1;
}

bool is_airborne() { return g_tel.valid && g_tel.h > 20; }
bool is_grounded() { return g_tel.valid && g_tel.h <= 5; }

// Send `cmd` several times to guarantee receipt over lossy WiFi. Used for
// latching commands (land) where the drone continues the maneuver on its own.
void send_burst(const char* cmd, int times, uint32_t gap_ms) {
    for (int i = 0; i < times; ++i) { send_command(cmd); sleep_ms(gap_ms); }
}

// Resend `cmd` until done() is telemetry-confirmed or we time out. Ignores the
// Tello's slow/duplicate acks entirely (they falsely reported failure); the
// only early-out is an "error" reply to the FIRST attempt, e.g. takeoff refused
// on low battery. Blocks up to timeout_ms — discrete actions only.
bool send_until(const char* cmd, uint32_t timeout_ms, bool (*done)()) {
    g_ack = 0;
    uint32_t elapsed = 0;
    bool first = true;
    while (elapsed < timeout_ms) {
        send_command(cmd);
        for (int i = 0; i < 8; ++i) {            // ~400ms per attempt
            if (done() || g_ack == 1) return true;  // effect seen, or drone ok'd
            if (first && g_ack == 2) return false;  // refused up front
            sleep_ms(50);
            elapsed += 50;
        }
        first = false;
    }
    return done() || g_ack == 1;
}

}  // namespace

bool begin() {
    ip_addr_t drone;
    ipaddr_aton(TELLO_IP, &drone);

    cyw43_arch_lwip_begin();
    // Tear down sockets from a previous session, otherwise re-binding the
    // telemetry port fails and the app can't reconnect. (This was the
    // "can't reconnect after exiting" bug.)
    if (cmd_pcb)   { udp_remove(cmd_pcb);   cmd_pcb = nullptr; }
    if (state_pcb) { udp_remove(state_pcb); state_pcb = nullptr; }
    g_tel.valid = false;   // don't let stale telemetry mislead is_grounded()

    cmd_pcb = udp_new();
    state_pcb = udp_new();
    bool ok = cmd_pcb && state_pcb;
    if (ok) {
        udp_recv(cmd_pcb, cmd_recv, nullptr);
        udp_connect(cmd_pcb, &drone, CMD_PORT);        // fixes the remote peer
        udp_recv(state_pcb, state_recv, nullptr);
        ok = (udp_bind(state_pcb, IP_ANY_TYPE, STATE_PORT) == ERR_OK);
    }
    cyw43_arch_lwip_end();
    return ok;
}

bool enter_sdk_mode(uint32_t timeout_ms) {
    return send_reliable("command", timeout_ms);
}

void send_command(const char* cmd) { udp_send_str(cmd_pcb, cmd); }

void send_rc(int lr, int fb, int ud, int yaw) {
    char buf[32];
    snprintf(buf, sizeof(buf), "rc %d %d %d %d",
             clamp100(lr), clamp100(fb), clamp100(ud), clamp100(yaw));
    send_command(buf);
}

bool takeoff() {
    // Confirm by height rising, not by the (late, misleading) ack.
    return send_until("takeoff", 8000, is_airborne);
}
bool land() {
    // Latching auto-land: a TIGHT burst guarantees receipt, then we leave the
    // drone completely alone. Re-sending `land` mid-descent restarts the
    // landing sequence and it never touches down (it just hovers low) — that
    // was the "won't actually land" bug. Send once, hands off.
    send_burst("land", 3, 60);
    return true;
}
void emergency() {
    // Immediate motor cutoff — send a few times, no waiting, since this is the
    // "stop now" path and packet loss must not delay it.
    for (int i = 0; i < 3; ++i) { send_command("emergency"); sleep_ms(20); }
}

const Telemetry& telemetry() { return g_tel; }

const char* last_response() { return g_last_resp; }

void end() {
    cyw43_arch_lwip_begin();
    if (cmd_pcb)   { udp_remove(cmd_pcb);   cmd_pcb = nullptr; }
    if (state_pcb) { udp_remove(state_pcb); state_pcb = nullptr; }
    cyw43_arch_lwip_end();
    g_tel.valid = false;
}

bool link_fresh(uint32_t fresh_ms) {
    if (!g_tel.valid) return false;
    uint32_t now = to_ms_since_boot(get_absolute_time());
    return (now - g_tel.last_update_ms) <= fresh_ms;
}

}  // namespace tello
