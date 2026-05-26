#!/usr/bin/env python3
"""
Pico Simulator — run any pico_everything app on your Mac.

Usage:  python3 pico_sim.py <app_name>
Example: python3 pico_sim.py flappybird

Controls:
  Z=keyA   X=keyB   A=keyX   S=keyY
  Arrow keys=D-pad   Enter=ctrl   ESC=quit
"""

import pygame
import sys
import struct
import time as _real_time
import types

W = H = 240


# ── Colour conversion ──────────────────────────────────────────────────────────

def _c(color):
    """RGB565 as stored in Pico framebuf → pygame RGB tuple.
    ST7789 with MAD=0x70: standard G bits→display R, B bits→display G, R bits→display B."""
    r5 = (color >> 11) & 0x1F   # standard R bits → display Blue
    g6 = (color >> 5)  & 0x3F   # standard G bits → display Red
    b5 =  color        & 0x1F   # standard B bits → display Green
    return (g6 << 2 | g6 >> 4, b5 << 3 | b5 >> 2, r5 << 3 | r5 >> 2)


# ── framebuf mock (used by apps for sprites) ───────────────────────────────────

class _FrameBuffer:
    def __init__(self, buf, width, height, fmt=1):
        self._b = buf
        self.width = width
        self.height = height

    def pixel(self, x, y, color=None):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        i = (y * self.width + x) * 2
        if color is None:
            return struct.unpack_from('<H', self._b, i)[0]
        struct.pack_into('<H', self._b, i, color & 0xFFFF)

    def fill(self, color):
        p = struct.pack('<H', color & 0xFFFF)
        for i in range(0, len(self._b), 2):
            self._b[i] = p[0]; self._b[i + 1] = p[1]

    def fill_rect(self, x, y, w, h, color):
        for dy in range(h):
            for dx in range(w):
                self.pixel(x + dx, y + dy, color)

    def rect(self, x, y, w, h, color):
        for i in range(w):
            self.pixel(x + i, y, color)
            self.pixel(x + i, y + h - 1, color)
        for i in range(h):
            self.pixel(x, y + i, color)
            self.pixel(x + w - 1, y + i, color)

    def line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1); dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self.pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x1 += sx
            if e2 <  dx: err += dx; y1 += sy

    def blit(self, fb, x, y, key=-1):
        for py in range(fb.height):
            for px in range(fb.width):
                c = fb.pixel(px, py)
                if c != key:
                    self.pixel(x + px, y + py, c)

    def text(self, s, x, y, color):
        pass  # handled by _LCD


# ── LCD mock ───────────────────────────────────────────────────────────────────

_screen = None


def _handle_events():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()


class _LCD:
    def __init__(self):
        self._surf = pygame.Surface((W, H))
        self._font = None
        self.red   = 0x07E0
        self.green = 0x001F
        self.blue  = 0xF800
        self.white = 0xFFFF

    def _fnt(self):
        if not self._font:
            self._font = pygame.font.SysFont('monospace', 8)
        return self._font

    def fill(self, color):
        self._surf.fill(_c(color))

    def fill_rect(self, x, y, w, h, color):
        pygame.draw.rect(self._surf, _c(color), (x, y, w, h))

    def rect(self, x, y, w, h, color):
        pygame.draw.rect(self._surf, _c(color), (x, y, w, h), 1)

    def line(self, x1, y1, x2, y2, color):
        pygame.draw.line(self._surf, _c(color), (x1, y1), (x2, y2))

    def pixel(self, x, y, color=None):
        if color is not None and 0 <= x < W and 0 <= y < H:
            self._surf.set_at((x, y), _c(color))

    def text(self, s, x, y, color):
        self._surf.blit(self._fnt().render(str(s), False, _c(color)), (x, y))

    def blit(self, fb, x, y, key=-1):
        for py in range(fb.height):
            for px in range(fb.width):
                c = fb.pixel(px, py)
                if c != key:
                    rx, ry = x + px, y + py
                    if 0 <= rx < W and 0 <= ry < H:
                        self._surf.set_at((rx, ry), _c(c))

    def scroll(self, dx, dy):
        self._surf.scroll(dx, dy)

    def show(self):
        _handle_events()
        _screen.blit(self._surf, (0, 0))
        pygame.display.flip()


# ── Keys mock ─────────────────────────────────────────────────────────────────

class _Btn:
    def __init__(self, k):
        self._k = k

    def value(self):
        _handle_events()
        return 0 if pygame.key.get_pressed()[self._k] else 1


class _Keys:
    keyA  = _Btn(pygame.K_z)
    keyB  = _Btn(pygame.K_x)
    keyX  = _Btn(pygame.K_a)
    keyY  = _Btn(pygame.K_s)
    up    = _Btn(pygame.K_UP)
    down  = _Btn(pygame.K_DOWN)
    left  = _Btn(pygame.K_LEFT)
    right = _Btn(pygame.K_RIGHT)
    ctrl  = _Btn(pygame.K_RETURN)


# ── time mock (adds MicroPython extras) ───────────────────────────────────────

_t0 = _real_time.monotonic()

_time = types.ModuleType('time')
_time.sleep    = _real_time.sleep
_time.sleep_ms = lambda ms: _real_time.sleep(ms / 1000)
_time.sleep_us = lambda us: _real_time.sleep(us / 1_000_000)
_time.time     = _real_time.time
_time.ticks_ms   = lambda: int((_real_time.monotonic() - _t0) * 1000) & 0x3FFFFFFF
_time.ticks_diff = lambda new, old: (new - old) & 0x3FFFFFFF


# ── machine mock ──────────────────────────────────────────────────────────────

class _Pin:
    IN = OUT = PULL_UP = PULL_DOWN = 0
    def __init__(self, *a, **kw): pass
    def __call__(self, v=None): pass
    def value(self): return 1

class _PWM:
    def __init__(self, *a): pass
    def freq(self, f): pass
    def duty_u16(self, d): pass

class _SPI:
    def __init__(self, *a, **kw): pass
    def write(self, b): pass

_machine = types.ModuleType('machine')
_machine.Pin = _Pin
_machine.PWM = _PWM
_machine.SPI = _SPI


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    app_name = sys.argv[1].replace('.py', '').replace('apps/', '').replace('apps\\', '')

    pygame.init()

    global _screen
    _screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(f"Pico Sim: {app_name}  |  Z=A  X=B  A=X  S=Y  Arrows=D-pad  ESC=quit")

    lcd = _LCD()

    _lcd_lib = types.ModuleType('LCD_Lib')
    _lcd_lib.LCD = lcd
    _lcd_lib.BL  = 13

    _framebuf_mod = types.ModuleType('framebuf')
    _framebuf_mod.FrameBuffer = _FrameBuffer
    _framebuf_mod.RGB565    = 1
    _framebuf_mod.MONO_HLSB = 3
    _framebuf_mod.MONO_VLSB = 0

    _keys_mod = _Keys()

    sys.modules['LCD_Lib'] = _lcd_lib
    sys.modules['keys']    = _keys_mod
    sys.modules['time']    = _time
    sys.modules['machine'] = _machine
    sys.modules['framebuf'] = _framebuf_mod

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))
    sys.path.insert(0, os.path.dirname(__file__) or '.')

    app = __import__(app_name)
    if hasattr(app, 'run'):
        app.run()
    elif hasattr(app, 'main'):
        app.main()
    else:
        raise AttributeError(f"{app_name}.py has no run() or main() function")

    pygame.quit()


if __name__ == '__main__':
    import os
    main()
