#!/usr/bin/env python3
"""Generate stencil panel SVG for Russian word clock v2.

Uses USSR STENCIL font which has built-in stencil bridges for all
enclosed Cyrillic letters (О, В, А, Д, Б, Р, Ь, Я etc).
"""

import cairo
import math

GRID = [
    "ГДВАДЦАТЬГПЯТЬГЖ",
    "ЖГДЕСЯТЬГМИНУТГЖ",
    "ЧЕТВЕРТЬПОЛОВИНА",
    "ГБЕЗГДВАДЦАТИГЖГ",
    "ПЯТИГЧЕТВЕРТИГГГ",
    "ДЕСЯТИПЕРВОГОТРИ",
    "ВТОРОГОПЯТОГОЧАС",
    "ТРЕТЬЕГОШЕСТОГОГ",
    "ЧЕТВЁРТОГОЧЕТЫРЕ",
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
PITCH = 16.67  # mm between LED centers
MARGIN = 5.0   # mm border
PANEL_W = MARGIN * 2 + PITCH * COLS         # 276.72mm
DOT_ROW_Y = MARGIN + PITCH * ROWS + 20.0   # 20mm below grid
DOT_PAIR_SPACING = PITCH * 1.5               # within pair
DOT_GAP = PITCH * 3                          # between pairs
DOT_RADIUS = 3.0                            # mm
NUM_DOTS = 4
PANEL_H = DOT_ROW_Y + DOT_RADIUS + MARGIN  # ~304mm

FONT_FACE = "USSR STENCIL"
FONT_SIZE = 17.6  # mm — max inscribed in PITCH

BG_COLOR = (0.08, 0.08, 0.08)
LETTER_COLOR = (1.0, 1.0, 1.0)
FILLER_COLOR = (0.25, 0.25, 0.25)
CUT_STROKE = (0.8, 0.0, 0.0)
CUT_WIDTH = 0.15  # mm

# Active letter positions (non-filler)
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
    x = MARGIN + (col + 0.5) * PITCH
    y = MARGIN + (row + 0.5) * PITCH
    return x, y


def generate_svg():
    svg_path = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru/panel_stencil.svg"

    mm_to_pt = 72.0 / 25.4
    w_pt = PANEL_W * mm_to_pt
    h_pt = PANEL_H * mm_to_pt

    surface = cairo.SVGSurface(svg_path, w_pt, h_pt)
    ctx = cairo.Context(surface)
    ctx.scale(mm_to_pt, mm_to_pt)

    # Background
    ctx.set_source_rgb(*BG_COLOR)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.fill()

    # Cut border
    ctx.set_source_rgb(*CUT_STROKE)
    ctx.set_line_width(CUT_WIDTH)
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)

    for row in range(ROWS):
        for col in range(COLS):
            ch = GRID[row][col]
            cx, cy = cell_center(row, col)
            is_active = (row, col) in ACTIVE

            ext = ctx.text_extents(ch)
            x = cx - ext.width / 2 - ext.x_bearing
            y = cy - ext.height / 2 - ext.y_bearing

            ctx.new_path()
            ctx.move_to(x, y)
            ctx.text_path(ch)

            ctx.set_source_rgb(*LETTER_COLOR)
            ctx.set_fill_rule(cairo.FillRule.EVEN_ODD)
            ctx.fill_preserve()

            ctx.set_source_rgb(*CUT_STROKE)
            ctx.set_line_width(CUT_WIDTH * 0.5)
            ctx.stroke()

    # Dot indicators below grid: ●● [gap] ●●
    cx = PANEL_W / 2
    dot_xs = [
        cx - DOT_GAP / 2 - DOT_PAIR_SPACING,
        cx - DOT_GAP / 2,
        cx + DOT_GAP / 2,
        cx + DOT_GAP / 2 + DOT_PAIR_SPACING,
    ]

    for dx in dot_xs:
        dy = DOT_ROW_Y

        ctx.new_path()
        ctx.arc(dx, dy, DOT_RADIUS, 0, 2 * math.pi)

        ctx.set_source_rgb(*LETTER_COLOR)
        ctx.fill_preserve()

        ctx.set_source_rgb(*CUT_STROKE)
        ctx.set_line_width(CUT_WIDTH * 0.5)
        ctx.stroke()

    surface.finish()
    print(f"Done: {svg_path}  ({PANEL_W:.1f} × {PANEL_H:.1f} mm)")
    return svg_path


if __name__ == "__main__":
    svg = generate_svg()

    import shutil
    dst = "/home/medivack/Downloads/panel_stencil.svg"
    shutil.copy2(svg, dst)
    print(f"Copied to: {dst}")
