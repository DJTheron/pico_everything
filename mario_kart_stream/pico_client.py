import network
import socket
import struct
import uzlib
import asyncio
import framebuf
from machine import Pin
import time

from LCD_Lib import LCD
from keys import keyA, keyB, keyX, keyY, up, down, left, right

# --- config: edit these ---
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
SERVER_IP  = "YOUR_LAPTOP_IP"   # e.g. "192.168.1.42"
SERVER_PORT = 5000

GBA_W = 240
GBA_H = 160
# Vertical offset to center 160px frame in 240px display
Y_OFFSET = (240 - GBA_H) // 2   # = 40

# Button byte flags — must match server.py
PICO_A     = 0x01
PICO_B     = 0x02
PICO_X     = 0x04
PICO_Y     = 0x08
PICO_UP    = 0x10
PICO_DOWN  = 0x20
PICO_LEFT  = 0x40
PICO_RIGHT = 0x80


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    LCD.fill(0x0000)
    LCD.text("Connecting WiFi...", 10, 110, LCD.white)
    LCD.show()
    for _ in range(20):
        if wlan.isconnected():
            break
        time.sleep(0.5)
    if not wlan.isconnected():
        LCD.fill(0x0000)
        LCD.text("WiFi FAILED", 10, 110, LCD.red)
        LCD.show()
        raise RuntimeError("WiFi connection failed")
    ip = wlan.ifconfig()[0]
    LCD.fill(0x0000)
    LCD.text("WiFi OK", 10, 100, LCD.green)
    LCD.text(ip, 10, 120, LCD.white)
    LCD.show()
    time.sleep(1)
    return wlan


def read_buttons():
    state = 0
    if keyA.value() == 0:    state |= PICO_A
    if keyB.value() == 0:    state |= PICO_B
    if keyX.value() == 0:    state |= PICO_X
    if keyY.value() == 0:    state |= PICO_Y
    if up.value() == 0:      state |= PICO_UP
    if down.value() == 0:    state |= PICO_DOWN
    if left.value() == 0:    state |= PICO_LEFT
    if right.value() == 0:   state |= PICO_RIGHT
    return state


async def input_loop(writer):
    """Send button state 60 times/sec. Never waits on frame receipt."""
    while True:
        state = read_buttons()
        try:
            writer.write(bytes([state]))
            await writer.drain()
        except Exception:
            return
        await asyncio.sleep_ms(16)


async def frame_loop(reader):
    """Receive frames from server and push to display."""
    # Draw black bars once — they won't be overwritten by blit()
    LCD.fill(0x0000)
    LCD.show()

    # Reuse a single bytearray for the frame buffer to avoid GC pressure
    frame_buf = bytearray(GBA_W * GBA_H * 2)
    frame_fb = framebuf.FrameBuffer(frame_buf, GBA_W, GBA_H, framebuf.RGB565)

    while True:
        # Read 4-byte length header
        header = await reader.readexactly(4)
        compressed_len = struct.unpack(">I", header)[0]

        # Read compressed frame
        compressed = await reader.readexactly(compressed_len)

        # Decompress into frame_buf in-place
        decompressed = uzlib.decompress(compressed)
        frame_buf[:] = decompressed

        # Blit GBA frame into center of display and flush
        LCD.blit(frame_fb, 0, Y_OFFSET)
        LCD.show()

        await asyncio.sleep_ms(0)  # yield so input_loop can run


async def main():
    connect_wifi()

    LCD.fill(0x0000)
    LCD.text("Connecting to", 10, 100, LCD.white)
    LCD.text("server...", 10, 120, LCD.white)
    LCD.show()

    reader, writer = await asyncio.open_connection(SERVER_IP, SERVER_PORT)
    print("Connected to server")

    await asyncio.gather(
        input_loop(writer),
        frame_loop(reader),
    )


asyncio.run(main())
