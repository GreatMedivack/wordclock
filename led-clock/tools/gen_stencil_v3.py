#!/usr/bin/env python3
"""Generate stencil panel SVG for Russian word clock v2.

Uses USSR STENCIL font which has built-in stencil bridges for all
enclosed Cyrillic letters (О, В, А, Д, Б, Р, Ь, Я etc).
"""

import cairo
import math

GRID = [
    "КГДВАДЦАТЬПЯТЬБЖ",
    "БВКДЕСЯТЬМИНУТГЖ",
    "ЧЕТВЕРТЬПОЛОВИНА",
    "КГБЕЗПЯТИДЕСЯТИД",
    "ДВАДЦАТИЧЕТВЕРТИ",
    "КПЕРВОГОВТОРОГОГ",
    "ТРЕТЬЕГОДЕСЯТОГО",
    "ЧЕТВЁРТОГОПЯТОГО",
    "ШЕСТОГОСЕДЬМОГОК",
    "ВОСЬМОГОДЕВЯТОГО",
    "КГОДИННАДЦАТОГОД",
    "КГДВЕНАДЦАТОГОБД",
    "ЧАСДВАТРИЧЕТЫРЕК",
    "ШЕСТЬСЕМЬВОСЕМЬК",
    "ДЕВЯТЬДВЕНАДЦАТЬ",
    "КГБОДИННАДЦАТЬДП",
]

COLS = 16
ROWS = 16
PITCH = 16.67  # mm between LED centers
MARGIN = 5.0   # mm border
PANEL = MARGIN * 2 + PITCH * COLS  # 276.72mm

FONT_FACE = "USSR STENCIL"
FONT_SIZE = 10.0  # mm

BG_COLOR = (0.08, 0.08, 0.08)
LETTER_COLOR = (1.0, 1.0, 1.0)
FILLER_COLOR = (0.25, 0.25, 0.25)
CUT_STROKE = (0.8, 0.0, 0.0)
CUT_WIDTH = 0.15  # mm

# Active letter positions (non-filler)
ACTIVE = set()
ACTIVE_RANGES = {
    0: 12, 1: 11, 2: 16, 3: 13, 4: 16, 5: 14, 6: 16, 7: 16,
    8: 15, 9: 16, 10: 13, 11: 12, 12: 15, 13: 15, 14: 16, 15: 11,
}
for row, count in ACTIVE_RANGES.items():
    for col in range(count):
        ACTIVE.add((row, col))


def cell_center(row, col):
    x = MARGIN + (col + 0.5) * PITCH
    y = MARGIN + (row + 0.5) * PITCH
    return x, y


def generate_svg():
    svg_path = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru/panel_stencil.svg"

    mm_to_pt = 72.0 / 25.4
    w_pt = PANEL * mm_to_pt
    h_pt = PANEL * mm_to_pt

    surface = cairo.SVGSurface(svg_path, w_pt, h_pt)
    ctx = cairo.Context(surface)
    ctx.scale(mm_to_pt, mm_to_pt)

    # Background
    ctx.set_source_rgb(*BG_COLOR)
    ctx.rectangle(0, 0, PANEL, PANEL)
    ctx.fill()

    # Cut border
    ctx.set_source_rgb(*CUT_STROKE)
    ctx.set_line_width(CUT_WIDTH)
    ctx.rectangle(0, 0, PANEL, PANEL)
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

            # Fill with even-odd rule (stencil gaps are built into font glyphs)
            ctx.set_source_rgb(*LETTER_COLOR)
            ctx.set_fill_rule(cairo.FillRule.EVEN_ODD)
            ctx.fill_preserve()

            # Thin red cut outline
            ctx.set_source_rgb(*CUT_STROKE)
            ctx.set_line_width(CUT_WIDTH * 0.5)
            ctx.stroke()

    surface.finish()
    print(f"Done: {svg_path}")
    return svg_path


if __name__ == "__main__":
    svg = generate_svg()

    import shutil
    dst = "/home/medivack/Downloads/panel_stencil.svg"
    shutil.copy2(svg, dst)
    print(f"Copied to: {dst}")
