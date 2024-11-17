# ---------------------------------------------------------------------------
# Matrix Rain
# ---------------------------------------------------------------------------
# Challenge proposé sur le Discord de Docstring
# ---------------------------------------------------------------------------
# Auteur : Steph
# Date   : 13 octobre 2024
# ---------------------------------------------------------------------------

import curses
from colorsys import hls_to_rgb as hls2rgb
from dataclasses import dataclass
from random import choice, randrange

KATAKANA = tuple(chr(0x30A0 + i) for i in range(96))
PALETTE_START_INDEX, PALETTE_NB_COLORS = 16, 16
PALETTE_HUES = (140, 210, 270, 300, 340, 30, 60)


@dataclass
class K:
    char: str
    color: int


class Drop:
    def __init__(self, x: int, h: int):
        self.x, self.h, self.trail = x, h, tuple(K(" ", 0) for _ in range(h))
        self._reset()

    def _reset(self):
        self.y = 0
        self.t = self.n = randrange(10)

    def _darken(self):
        for y in range(self.h):
            k = self.trail[y]
            if k.color > 0:
                k.color -= 1

    def _fall(self):
        k = self.trail[self.y]
        k.char = choice(KATAKANA)
        k.color = PALETTE_NB_COLORS - 1
        if self.y < self.h - 1:
            self.y += 1
        else:
            self._reset()

    def update(self):
        if self.t > 0:
            self.t -= 1
        else:
            self.t = self.n
            self._darken()
            self._fall()

    def draw(self, screen: curses.window):
        for y in range(self.h):
            k = self.trail[y]
            screen.addch(y, self.x * 2, k.char, curses.color_pair(PALETTE_START_INDEX + k.color))  # fmt: off


class Matrix:
    _singleton = None
    _initialized = False

    def __new__(cls, screen: curses.window):
        if not cls._singleton:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self, screen: curses.window):
        if Matrix._initialized:
            return
        Matrix._initialized = True
        h, w = screen.getmaxyx()
        screen.nodelay(True)
        self.screen = screen
        self.hue_index = 0
        self.drops = tuple(Drop(x, h - (1 if not w & 1 and x == (w >> 1) - 1 else 0)) for x in range(w >> 1))  # fmt:off
        curses.curs_set(0)
        curses.start_color()
        curses.init_color(0, 0, 0, 0)
        self._change_colors()
        for i in range(PALETTE_NB_COLORS):
            curses.init_pair(ci := PALETTE_START_INDEX + i, ci, 0)
        self._rain()

    def _change_colors(self):
        hue, n = (PALETTE_HUES[self.hue_index] % 360) / 359, PALETTE_NB_COLORS - 1  # fmt: off
        for i in range(PALETTE_NB_COLORS):
            ci = PALETTE_START_INDEX + i
            curses.init_color(ci, *(round(1000 * c) for c in hls2rgb(hue, 1 if i == n else .8 * i / n, 1)))  # fmt: off
        self.hue_index = (self.hue_index + 1) % len(PALETTE_HUES)

    def _rain(self):
        delay, looping = 1 << 3, True
        while looping:
            # fmt: off
            if ch := self.screen.getch():
                if   ch in {ord("q"), ord("Q")}:        looping = False        # noqa: E701
                elif ch == ord("+") and delay > 1:      delay >>= 1            # noqa: E701
                elif ch == ord("-") and delay < 1 << 8: delay <<= 1            # noqa: E701
                elif ch in {ord("c"), ord("C")}:        self._change_colors()  # noqa: E701
            # fmt: on
            for drop in self.drops:
                drop.update()
                drop.draw(self.screen)
            self.screen.refresh()
            self.screen.timeout(delay)


if __name__ == "__main__":
    curses.wrapper(Matrix)
