#!/usr/bin/env python3
"""Generate laser-cutting SVG for the clock front mask.

Output: red hairline strokes only (no fills, no background).
Convention: red (255,0,0) = cut, blue = engrave. Most laser shops accept this.
"""

import cairo
import ctypes
import math
import os
import shutil

# Register the project font with fontconfig so cairo finds it by family name
_FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "arduino", "wordclock_ru", "BlackOpsOne.ttf")
ctypes.CDLL("libfontconfig.so.1").FcConfigAppFontAddFile(None, _FONT_FILE.encode())

GRID = [
    "РДВАДЦАТЬЗПЯТЬЧЖ",
    "ФЭДЕСЯТЬЫМИНУТКЩ",
    "ЧЕТВЕРТЬПОЛОВИНА",
    "ЮБЕЗЛДВАДЦАТИМУП",
    "ПЯТИХЧЕТВЕРТИШЦЪ",
    "ДЕСЯТИПЕРВОГОТРИ",
    "ВТОРОГОПЯТОГОЧАС",
    "ТРЕТЬЕГОШЕСТОГОБ",
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
PITCH = 16.67       # mm between LED centers
MARGIN = 5.0        # mm border
PANEL_W = MARGIN * 2 + PITCH * COLS
GRID_BOTTOM = MARGIN + PITCH * ROWS
DOT_ROW_Y = GRID_BOTTOM + 18.0
DOT_RADIUS = 5.0
PANEL_H = DOT_ROW_Y + DOT_RADIUS + MARGIN

FONT_FACE = "Black Ops One"
FONT_SIZE = 15.0  # widest glyph Ж ≈ 15.8mm at this size, fits 16.67mm pitch

CUT_COLOR = (1.0, 0.0, 0.0)
CUT_WIDTH = 0.3      # mm — visible in preview; laser software uses color, not width


def cell_center(row, col):
    return MARGIN + (col + 0.5) * PITCH, MARGIN + (row + 0.5) * PITCH


def dot_xs():
    return [
        cell_center(0, 5)[0],
        cell_center(0, 6)[0],
        cell_center(0, 9)[0],
        cell_center(0, 10)[0],
    ]


def generate(svg_path):
    mm_to_pt = 72.0 / 25.4
    surface = cairo.SVGSurface(svg_path, PANEL_W * mm_to_pt, PANEL_H * mm_to_pt)
    ctx = cairo.Context(surface)
    ctx.scale(mm_to_pt, mm_to_pt)

    ctx.set_source_rgb(*CUT_COLOR)
    ctx.set_line_width(CUT_WIDTH)

    # Outer border — cut rectangle
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    # Letter outlines — cut paths
    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            ch = GRID[r][c]

            ext = ctx.text_extents(ch)
            x = cx - ext.width / 2 - ext.x_bearing
            y = cy - ext.height / 2 - ext.y_bearing

            ctx.new_path()
            ctx.move_to(x, y)
            ctx.text_path(ch)
            ctx.stroke()

    # Dot circles — cut
    for dx in dot_xs():
        ctx.new_path()
        ctx.arc(dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.stroke()

    surface.finish()
    print(f"Laser cut SVG: {svg_path}")
    print(f"  Panel: {PANEL_W:.1f} x {PANEL_H:.1f} mm")
    print(f"  All lines: red hairline ({CUT_WIDTH}mm) = cut")


if __name__ == "__main__":
    base = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru"
    out = f"{base}/laser_cut_mask.svg"
    generate(out)

    dst = "/home/medivack/Downloads/laser_cut_mask.svg"
    shutil.copy2(out, dst)
    print(f"Copied to: {dst}")
