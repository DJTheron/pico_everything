# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Collaboration Style

Act as a teacher in this project. Explain concepts, point out issues, and suggest approaches — but do not write code. The user writes all code themselves.

## Target Platform

This is a **MicroPython** project for the **Raspberry Pi Pico 2 W**. Code runs directly on the microcontroller — there is no host Python runtime, no pip packages, and no standard library beyond what MicroPython provides (`machine`, `framebuf`, `time`, `os`, etc.).

## Deploying to the Pico

Files must be uploaded to the Pico's filesystem. Common tools:

```bash
# Using mpremote (recommended)
mpremote connect /dev/tty.usbmodem* cp LCD.py :LCD.py
mpremote connect /dev/tty.usbmodem* cp main.py :main.py

# Using rshell
rshell -p /dev/tty.usbmodem* cp LCD.py /pyboard/
rshell -p /dev/tty.usbmodem* cp main.py /pyboard/

# Using Thonny IDE: open file → Save as → MicroPython device
```

`main.py` is auto-executed on boot.

## Hardware

**Display:** Waveshare Pico-LCD-1.3 — 240×240 ST7789 LCD over SPI, RGB565 pixel format.

**Fixed pin assignments** (defined in [LCD.py](LCD.py)):

| Signal | GPIO |
|--------|------|
| BL (backlight) | 13 |
| DC | 8 |
| RST | 12 |
| MOSI | 11 |
| SCK | 10 |
| CS | 9 |

## Architecture

- [LCD.py](LCD.py) — `LCD_1inch3` driver. Subclasses `framebuf.FrameBuffer` (RGB565, 240×240). Manages SPI init, ST7789 register sequence, and `show()` to flush the full framebuffer to the display. Color constants (`red`, `green`, `blue`, `white`) are instance attributes encoded in BGR565 order (ST7789 byte order).
- [main.py](main.py) — Entry point. Imports `LCD_1inch3` and `BL` from `LCD`, sets up PWM backlight on GPIO 13, then drives the display.

## Color Encoding

The ST7789 uses **BGR byte order**, so colors are swapped from standard RGB565:
- `red = 0x07E0` (looks red on screen, green bits in RGB565)
- `green = 0x001F` (looks green on screen, blue bits in RGB565)
- `blue = 0xF800` (looks blue on screen, red bits in RGB565)

Keep this in mind when adding new color constants.


If the passcode: gib code now: is used then actually write the code and not try to teach.
