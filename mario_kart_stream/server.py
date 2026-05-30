import socket
import struct
import zlib
import time
import os
import sys

try:
    import mgba.core
    import mgba.image
    import numpy as np
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# --- config ---
ROM_PATH = os.path.join(os.path.dirname(__file__), "..", "Mario Kart - Super Circuit (Europe).gba")
HOST = "0.0.0.0"
PORT = 5000
TARGET_FPS = 30
GBA_W = 240
GBA_H = 160

# GBA key bitmask (mGBA standard)
GBA_A      = 0x001
GBA_B      = 0x002
GBA_SELECT = 0x004
GBA_START  = 0x008
GBA_RIGHT  = 0x010
GBA_LEFT   = 0x020
GBA_UP     = 0x040
GBA_DOWN   = 0x080
GBA_R      = 0x100
GBA_L      = 0x200

# Pico button byte sent by client (1 byte, matches pico_client.py)
PICO_A     = 0x01
PICO_B     = 0x02
PICO_X     = 0x04   # → GBA R
PICO_Y     = 0x08   # → GBA L
PICO_UP    = 0x10
PICO_DOWN  = 0x20
PICO_LEFT  = 0x40
PICO_RIGHT = 0x80


def pico_to_gba(byte):
    keys = 0
    if byte & PICO_A:     keys |= GBA_A
    if byte & PICO_B:     keys |= GBA_B
    if byte & PICO_X:     keys |= GBA_R
    if byte & PICO_Y:     keys |= GBA_L
    if byte & PICO_UP:    keys |= GBA_UP
    if byte & PICO_DOWN:  keys |= GBA_DOWN
    if byte & PICO_LEFT:  keys |= GBA_LEFT
    if byte & PICO_RIGHT: keys |= GBA_RIGHT
    return keys


def frame_to_rgb565_bytes(image):
    """
    Convert mGBA image to big-endian RGB565 bytes for the ST7789 display.
    mGBA's Image buffer is BGRA (4 bytes/pixel) on little-endian systems.
    We use numpy for speed — this runs in under 1ms on a modern laptop.
    """
    # mgba.image.Image supports the buffer protocol as BGRA8888
    raw = np.frombuffer(image, dtype=np.uint8).reshape(GBA_H, GBA_W, 4)
    b = raw[:, :, 0].astype(np.uint16)
    g = raw[:, :, 1].astype(np.uint16)
    r = raw[:, :, 2].astype(np.uint16)
    # Pack into RGB565 (big-endian so ST7789 reads correctly)
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return rgb565.astype(">u2").tobytes()


def recv_exact(conn, n):
    buf = bytearray(n)
    view = memoryview(buf)
    pos = 0
    while pos < n:
        received = conn.recv_into(view[pos:], n - pos)
        if not received:
            raise ConnectionResetError("Client disconnected")
        pos += received
    return bytes(buf)


def run():
    print(f"Loading ROM: {ROM_PATH}")
    core = mgba.core.load_path(ROM_PATH)
    if core is None:
        raise RuntimeError(f"Failed to load ROM at: {ROM_PATH}")

    core.reset()
    w, h = core.desired_video_dimensions()
    print(f"GBA resolution: {w}x{h}")

    image = mgba.image.Image(w, h)
    core.set_video_buffer(image)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(1)
    print(f"Waiting for Pico on port {PORT}...")

    conn, addr = server_sock.accept()
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    conn.setblocking(False)
    print(f"Pico connected from {addr}")

    frame_interval = 1.0 / TARGET_FPS
    current_keys = 0
    frame_count = 0
    t_start = time.time()

    while True:
        t0 = time.perf_counter()

        # Drain any pending input (non-blocking, take the last byte received)
        try:
            while True:
                data = conn.recv(64)
                if not data:
                    raise ConnectionResetError
                current_keys = pico_to_gba(data[-1])
                core.set_keys(current_keys)
        except BlockingIOError:
            pass

        # Advance emulator one frame
        core.run_frame()

        # Convert frame to RGB565 and compress
        frame_bytes = frame_to_rgb565_bytes(image)
        compressed = zlib.compress(frame_bytes, level=1)  # level 1 = fastest

        # Send: 4-byte big-endian length, then compressed data
        conn.setblocking(True)
        try:
            conn.sendall(struct.pack(">I", len(compressed)) + compressed)
        except (BrokenPipeError, ConnectionResetError):
            print("Pico disconnected")
            break
        conn.setblocking(False)

        frame_count += 1
        if frame_count % (TARGET_FPS * 5) == 0:
            elapsed = time.time() - t_start
            print(f"  {frame_count / elapsed:.1f} fps  |  frame {frame_count}")

        # Pace to target FPS
        elapsed = time.perf_counter() - t0
        wait = frame_interval - elapsed
        if wait > 0:
            time.sleep(wait)


if __name__ == "__main__":
    run()
