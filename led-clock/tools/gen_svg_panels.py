#!/usr/bin/env python3
"""Regenerate panel_front.svg, baffle_grid.svg, cutting_template.svg with dot row.

Uses Cairo to convert text to paths so Black Ops One font is embedded.

Geometry v3 (30×30cm board):
  - Panel 300×300 mm.
  - 16×16 letter grid: 1.8cm top/bottom margins → vertical pitch 16.5mm.
    Horizontal pitch stays native 16.67mm (60/m strip), grid centered → ~16.6mm side margins.
  - 6-LED dot strip under grid columns 6-11, 5mm gap below the grid.
    Lit pairs under cols 6,7 (idx 256,257) and 10,11 (idx 260,261);
    middle two under cols 8,9 (idx 258,259) stay dark as a visible separator.
"""

import cairo
import ctypes
import math
import os

# Register the project font with fontconfig so cairo finds it by family name
_FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "arduino", "wordclock_ru", "BlackOpsOne.ttf")
ctypes.CDLL("libfontconfig.so.1").FcConfigAppFontAddFile(None, _FONT_FILE.encode())

GRID = [
    "ЪДВАДЦАТЬНПЯТЬИЧ",
    "РЦДЕСЯТЬГМИНУТЛЗ",
    "ЧЕТВЕРТЬПОЛОВИНА",
    "ЭБЕЗХДВАДЦАТИПСК",
    "ПЯТИУЧЕТВЕРТИАЯБ",
    "ДЕСЯТИПЕРВОГОТРИ",
    "ВТОРОГОПЯТОГОЧАС",
    "ТРЕТЬЕГОШЕСТОГОВ",
    "ЧЕТВЕРТОГОЧЕТЫРЕ",
    "СЕДЬМОГОВОСЬМОГО",
    "ДЕВЯТОГОДЕСЯТОГО",
    "ОДИННАДЦАТОГОДВА",
    "ДВЕНАДЦАТОГОПЯТЬ",
    "ДВЕНАДЦАТЬДЕСЯТЬ",
    "ОДИННАДЦАТЬШЕСТЬ",
    "СЕМЬВОСЕМЬДЕВЯТЬ",
]

COLS = 16
ROWS = 16

# Panel is the physical 30×30cm board
PANEL_W = 300.0
PANEL_H = 300.0

# Horizontal: native strip pitch (60 LED/m), grid centered on the panel
PITCH_X = 16.67
MARGIN_X = (PANEL_W - PITCH_X * COLS) / 2.0   # ≈ 16.64mm side margins

# Vertical: 1.8cm top/bottom margins around the 16 rows fix the pitch
MARGIN_TOP = 18.0
PITCH_Y = (PANEL_H - 2 * MARGIN_TOP) / ROWS   # = 16.5mm
GRID_BOTTOM = MARGIN_TOP + PITCH_Y * ROWS     # = 282mm

# 6-LED dot strip below the grid
DOT_GAP = 5.0                                 # 0.5cm gap grid→dots
DOT_RADIUS = 5.0
DOT_ROW_Y = GRID_BOTTOM + DOT_GAP + DOT_RADIUS  # center = 292mm (3mm to bottom edge)
DOT_COLS = list(range(5, 11))                 # under grid columns 5..10 (centered)
DOT_LIT_COLS = {5, 6, 9, 10}                  # lit pairs; 7,8 are the dark gap
NUM_DOTS = len(DOT_COLS)

FONT_FACE = "Black Ops One"
FONT_SIZE = 15.0  # widest glyph Ж ≈ 15.8mm at this size, fits the pitch
MONO_FACE = "monospace"
MONO_SIZE = 3.5

MM_TO_PT = 72.0 / 25.4

ACTIVE = set()
_WORD_RANGES = [
    (0, 1, 9), (0, 10, 14),
    (1, 2, 8), (1, 9, 14),
    (2, 0, 8), (2, 8, 16),
    (3, 1, 4), (3, 5, 13),
    (4, 0, 4), (4, 5, 13),
    (5, 0, 6), (5, 6, 13), (5, 13, 16),
    (6, 0, 7), (6, 7, 13), (6, 13, 16),
    (7, 0, 8), (7, 8, 15),
    (8, 0, 10), (8, 10, 16),
    (9, 0, 8), (9, 8, 16),
    (10, 0, 8), (10, 8, 16),
    (11, 0, 13), (11, 13, 16),
    (12, 0, 12), (12, 12, 16),
    (13, 0, 10), (13, 10, 16),
    (14, 0, 11), (14, 11, 16),
    (15, 0, 4), (15, 4, 10), (15, 10, 16),
]
for row, cs, ce in _WORD_RANGES:
    for col in range(cs, ce):
        ACTIVE.add((row, col))


def cell_center(row, col):
    return MARGIN_X + (col + 0.5) * PITCH_X, MARGIN_TOP + (row + 0.5) * PITCH_Y


def dot_xs():
    """X centers of the 6 dot LEDs, left→right, aligned to grid cols 6..11."""
    return [MARGIN_X + (c + 0.5) * PITCH_X for c in DOT_COLS]


def dot_is_lit(i):
    return DOT_COLS[i] in DOT_LIT_COLS


def led_index(row, col):
    if row % 2 == 0:
        return row * 16 + col
    else:
        return row * 16 + (15 - col)


def _draw_grid_lines(ctx, ox=0):
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.set_line_width(0.1)
    for r in range(ROWS + 1):
        y = MARGIN_TOP + r * PITCH_Y
        ctx.move_to(ox + MARGIN_X, y)
        ctx.line_to(ox + PANEL_W - MARGIN_X, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = ox + MARGIN_X + c * PITCH_X
        ctx.move_to(x, MARGIN_TOP)
        ctx.line_to(x, GRID_BOTTOM)
        ctx.stroke()


def _draw_text_centered(ctx, cx, cy, ch, ref=None):
    """Center ch horizontally; vertically align by ref glyph's box so all
    letters share a common baseline/top edge (ref=None: self-centered)."""
    ext = ctx.text_extents(ch)
    vext = ctx.text_extents(ref) if ref else ext
    x = cx - ext.width / 2 - ext.x_bearing
    y = cy - vext.height / 2 - vext.y_bearing
    ctx.move_to(x, y)
    ctx.text_path(ch)


def generate_panel_front(path):
    surface = cairo.SVGSurface(path, PANEL_W * MM_TO_PT, PANEL_H * MM_TO_PT)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)

    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.fill()

    ctx.set_source_rgb(0.8, 0, 0)
    ctx.set_line_width(0.2)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    _draw_grid_lines(ctx)

    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            _draw_text_centered(ctx, cx, cy, GRID[r][c], ref="Н")
            if (r, c) in ACTIVE:
                ctx.set_source_rgb(1, 1, 1)
            else:
                ctx.set_source_rgb(0.33, 0.33, 0.33)
            ctx.fill()

    for i, dx in enumerate(dot_xs()):
        if not dot_is_lit(i):
            continue  # no opening under the dark separator dots (258,259)
        ctx.arc(dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.set_line_width(0.1)
        ctx.stroke()

    surface.finish()


def generate_baffle_grid(path):
    surface = cairo.SVGSurface(path, PANEL_W * MM_TO_PT, PANEL_H * MM_TO_PT)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)

    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.fill()

    ctx.set_source_rgb(0.8, 0, 0)
    ctx.set_line_width(0.2)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    ctx.set_source_rgb(0, 0, 1)
    ctx.set_line_width(0.15)
    for r in range(ROWS + 1):
        y = MARGIN_TOP + r * PITCH_Y
        ctx.move_to(MARGIN_X, y)
        ctx.line_to(PANEL_W - MARGIN_X, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = MARGIN_X + c * PITCH_X
        ctx.move_to(x, MARGIN_TOP)
        ctx.line_to(x, GRID_BOTTOM)
        ctx.stroke()

    ctx.select_font_face(MONO_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(MONO_SIZE)
    ctx.set_source_rgb(0.6, 0.6, 0.6)

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            idx = str(led_index(r, c))
            _draw_text_centered(ctx, cx, cy, idx)
            ctx.fill()

    for i, dx in enumerate(dot_xs()):
        ctx.arc(dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.set_source_rgb(0, 0, 1)
        ctx.set_line_width(0.15)
        ctx.stroke()
        idx = str(256 + i)
        _draw_text_centered(ctx, dx, DOT_ROW_Y, idx)
        ctx.set_source_rgb(0.6, 0.6, 0.6)
        ctx.fill()

    surface.finish()


def generate_cutting_template(path):
    GAP = 10.0
    TOTAL_W = PANEL_W * 2 + GAP

    surface = cairo.SVGSurface(path, TOTAL_W * MM_TO_PT, PANEL_H * MM_TO_PT)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)

    ctx.set_source_rgb(0.96, 0.96, 0.96)
    ctx.rectangle(0, 0, TOTAL_W, PANEL_H)
    ctx.fill()

    # Left: front view
    ox = 0
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.rectangle(ox, 0, PANEL_W, PANEL_H)
    ctx.fill()
    ctx.set_source_rgb(0.8, 0, 0)
    ctx.set_line_width(0.2)
    ctx.rectangle(ox, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    _draw_grid_lines(ctx, ox)

    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            _draw_text_centered(ctx, ox + cx, cy, GRID[r][c], ref="Н")
            if (r, c) in ACTIVE:
                ctx.set_source_rgb(1, 1, 1)
            else:
                ctx.set_source_rgb(0.33, 0.33, 0.33)
            ctx.fill()

    for i, dx in enumerate(dot_xs()):
        if not dot_is_lit(i):
            continue  # no opening under the dark separator dots (258,259)
        ctx.arc(ox + dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.set_line_width(0.1)
        ctx.stroke()

    # Right: baffle (LED indices)
    ox = PANEL_W + GAP
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(ox, 0, PANEL_W, PANEL_H)
    ctx.fill()
    ctx.set_source_rgb(0.8, 0, 0)
    ctx.set_line_width(0.2)
    ctx.rectangle(ox, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    ctx.set_source_rgb(0, 0, 1)
    ctx.set_line_width(0.15)
    for r in range(ROWS + 1):
        y = MARGIN_TOP + r * PITCH_Y
        ctx.move_to(ox + MARGIN_X, y)
        ctx.line_to(ox + PANEL_W - MARGIN_X, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = ox + MARGIN_X + c * PITCH_X
        ctx.move_to(x, MARGIN_TOP)
        ctx.line_to(x, GRID_BOTTOM)
        ctx.stroke()

    ctx.select_font_face(MONO_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(MONO_SIZE)
    ctx.set_source_rgb(0.6, 0.6, 0.6)

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            idx = str(led_index(r, c))
            _draw_text_centered(ctx, ox + cx, cy, idx)
            ctx.fill()

    for i, dx in enumerate(dot_xs()):
        ctx.arc(ox + dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.set_source_rgb(0, 0, 1)
        ctx.set_line_width(0.15)
        ctx.stroke()
        idx = str(256 + i)
        _draw_text_centered(ctx, ox + dx, DOT_ROW_Y, idx)
        ctx.set_source_rgb(0.6, 0.6, 0.6)
        ctx.fill()

    surface.finish()


if __name__ == "__main__":
    base = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru"

    for name, gen in [("panel_front.svg", generate_panel_front),
                      ("baffle_grid.svg", generate_baffle_grid),
                      ("cutting_template.svg", generate_cutting_template)]:
        path = f"{base}/{name}"
        gen(path)
        print(f"  {name}: {PANEL_W:.2f} x {PANEL_H:.2f} mm")

    print(f"\nGeometry: pitch X={PITCH_X} Y={PITCH_Y:.2f}mm, "
          f"margins side={MARGIN_X:.2f} top/bottom={MARGIN_TOP}mm")
    print(f"All SVGs updated with {NUM_DOTS} dot indicators (lit cols {sorted(DOT_LIT_COLS)}).")
