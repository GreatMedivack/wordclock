#!/usr/bin/env python3
"""Visualize any word clock grid (EN/RU/JA) with highlighted active words.

Usage:
    python grid_visualizer.py                          — EN, 3:47 PM
    python grid_visualizer.py --lang ru --time "5:27 PM"
    python grid_visualizer.py --lang ja --time "11:03 AM"
    python grid_visualizer.py --wiring --lang ja
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "micropython"))

from lang.grid_en import GRID as GRID_EN, COLS as COLS_EN, HOURS as H_EN, AMPM as A_EN, TENS as T_EN, ONES as O_EN, FIXED as F_EN
from lang.grid_ru import GRID as GRID_RU, COLS as COLS_RU, HOURS as H_RU, AMPM as A_RU, TENS as T_RU, ONES as O_RU, FIXED as F_RU
from lang.grid_ja import GRID as GRID_JA, COLS as COLS_JA, HOURS as H_JA, AMPM as A_JA, TENS as T_JA, ONES as O_JA, FIXED as F_JA

LANGS = {
    "en": (GRID_EN, COLS_EN, H_EN, A_EN, T_EN, O_EN, F_EN),
    "ru": (GRID_RU, COLS_RU, H_RU, A_RU, T_RU, O_RU, F_RU),
    "ja": (GRID_JA, COLS_JA, H_JA, A_JA, T_JA, O_JA, F_JA),
}


def active_positions(lang, hour12, tens, ones, ampm_str):
    grid, cols, hours, ampm, tens_m, ones_m, fixed = LANGS[lang]
    active = set()
    for mapping, key in [(hours, hour12), (tens_m, tens), (ones_m, ones), (ampm, ampm_str)]:
        row, cs, ce = mapping[key]
        for c in range(cs, ce):
            active.add((row, c))
    for pos in fixed:
        row, cs, ce = pos
        for c in range(cs, ce):
            active.add((row, c))
    return active


def is_wide_char(ch):
    cp = ord(ch)
    return (cp >= 0x2E80 and cp <= 0x9FFF) or (cp >= 0x3000 and cp <= 0x303F) or (cp >= 0xFF00)


def print_grid(lang, hour12=3, tens=4, ones=7, ampm_str="PM"):
    grid, cols, *_ = LANGS[lang]
    active = active_positions(lang, hour12, tens, ones, ampm_str)
    print(f"\n  [{lang.upper()}] {hour12}:{tens}{ones} {ampm_str}\n")
    for r, row_text in enumerate(grid):
        line = "  "
        for c, ch in enumerate(row_text):
            pad = " " if is_wide_char(ch) else "  "
            if (r, c) in active:
                line += f"\033[97;42m{pad[:-1]}{ch} \033[0m"
            else:
                line += f"\033[90m{pad[:-1]}{ch} \033[0m"
        print(line)
    print()


def led_index(cols, row, col):
    if row % 2 == 0:
        return row * cols + col
    return row * cols + (cols - 1 - col)


def print_wiring(lang):
    grid, cols, *_ = LANGS[lang]
    rows = len(grid)
    print(f"\n  [{lang.upper()}] LED index map ({rows}×{cols} = {rows * cols} LEDs):\n")
    print("  " + "".join(f"{c:>4}" for c in range(cols)))
    print("  " + "─" * (cols * 4))
    for r in range(rows):
        indices = [led_index(cols, r, c) for c in range(cols)]
        d = "→" if r % 2 == 0 else "←"
        print(f"{r:2}│" + "".join(f"{i:>4}" for i in indices) + f"  {d}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Word clock grid visualizer")
    parser.add_argument("--lang", choices=["en", "ru", "ja"], default="en")
    parser.add_argument("--wiring", action="store_true")
    parser.add_argument("--time", default="3:47 PM")
    args = parser.parse_args()

    if args.wiring:
        print_wiring(args.lang)
        return

    parts = args.time.replace(":", " ").split()
    hour12 = int(parts[0])
    minute = int(parts[1])
    ampm_str = parts[2].upper()
    print_grid(args.lang, hour12, minute // 10, minute % 10, ampm_str)


if __name__ == "__main__":
    main()
