#!/usr/bin/env python3
"""Generate an A3 print PDF of the clock face at true 1:1 (mm).

The full board is 300x300mm and does not fit A3 (297x420). This crops the sheet to
the letter grid plus a 5mm margin around the outermost letters/dots, then centres that
on a portrait A3 page — so "print at 100% / actual size" lands dead-on 1:1. The clock
face is filled: a black panel with the letters and minute dots knocked out to white
(paper), matching the on-screen stencil render.
"""

import cairo
import ctypes
import math
import os
import shutil

import glyph_fix

_FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "arduino", "wordclock_ru", "BlackOpsOne.ttf")
ctypes.CDLL("libfontconfig.so.1").FcConfigAppFontAddFile(None, _FONT_FILE.encode())

GRID = [
    "ЪДВАДЦАТЬНПЯТЬИЧ", "РЦДЕСЯТЬГМИНУТЛЗ", "ЧЕТВЕРТЬПОЛОВИНА", "ЭБЕЗХДВАДЦАТИПСК",
    "ПЯТИУЧЕТВЕРТИАЯБ", "ДЕСЯТИПЕРВОГОТРИ", "ВТОРОГОПЯТОГОЧАС", "ТРЕТЬЕГОШЕСТОГОВ",
    "ЧЕТВЕРТОГОЧЕТЫРЕ", "СЕДЬМОГОВОСЬМОГО", "ДЕВЯТОГОДЕСЯТОГО", "ОДИННАДЦАТОГОДВА",
    "ДВЕНАДЦАТОГОПЯТЬ", "ДВЕНАДЦАТЬДЕСЯТЬ", "ОДИННАДЦАТЬШЕСТЬ", "СЕМЬВОСЕМЬДЕВЯТЬ",
]
COLS = ROWS = 16
PANEL_W = PANEL_H = 300.0
PITCH_X = 16.67
MARGIN_X = (PANEL_W - PITCH_X * COLS) / 2.0
MARGIN_TOP = 18.0
PITCH_Y = (PANEL_H - 2 * MARGIN_TOP) / ROWS
GRID_BOTTOM = MARGIN_TOP + PITCH_Y * ROWS
DOT_GAP = 5.0
DOT_RADIUS = 5.0
DOT_ROW_Y = GRID_BOTTOM + DOT_GAP + DOT_RADIUS
DOT_LIT_COLS = [5, 6, 9, 10]

FONT_SIZE = 15.0
LINE_W = 0.3            # mm — visible when printed (laser file keeps its own hairline)
CROP_MARGIN = 5.0      # mm kept around the outermost letters/dots

A3_W, A3_H = 297.0, 420.0
MM_TO_PT = 72.0 / 25.4


def cell_center(row, col):
    return MARGIN_X + (col + 0.5) * PITCH_X, MARGIN_TOP + (row + 0.5) * PITCH_Y


def glyph_xy(ctx, ref, ch, cx, cy):
    ext = ctx.text_extents(ch)
    return cx - ext.width / 2 - ext.x_bearing, cy - ref.height / 2 - ref.y_bearing


def dot_xs():
    return [cell_center(0, c)[0] for c in DOT_LIT_COLS]


def content_bounds(ctx, ref):
    minx = miny = 1e9
    maxx = maxy = -1e9
    for r in range(ROWS):
        for c in range(COLS):
            ch = GRID[r][c]
            cx, cy = cell_center(r, c)
            x, y = glyph_xy(ctx, ref, ch, cx, cy)
            bx0, by0, bx1, by1 = glyph_fix.fixed_opening(ch, FONT_SIZE).bounds
            minx, maxx = min(minx, x + bx0), max(maxx, x + bx1)
            miny, maxy = min(miny, y + by0), max(maxy, y + by1)
    for dx in dot_xs():
        minx, maxx = min(minx, dx - DOT_RADIUS), max(maxx, dx + DOT_RADIUS)
        maxy = max(maxy, DOT_ROW_Y + DOT_RADIUS)
    return minx, miny, maxx, maxy


def draw(ctx):
    ctx.select_font_face("Black Ops One", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)
    ref = ctx.text_extents("Н")

    minx, miny, maxx, maxy = content_bounds(ctx, ref)
    crop = (minx - CROP_MARGIN, miny - CROP_MARGIN,
            maxx + CROP_MARGIN, maxy + CROP_MARGIN)
    crop_w = crop[2] - crop[0]
    crop_h = crop[3] - crop[1]

    # centre the crop rectangle on the A3 page
    ctx.translate((A3_W - crop_w) / 2 - crop[0], (A3_H - crop_h) / 2 - crop[1])

    # One even-odd path: black panel with letters/dots knocked out to paper.
    # Nesting parity does the rest — letter openings become white holes, and each
    # counter island (nested one level deeper) fills black again, exactly like the cut.
    ctx.set_line_join(cairo.LINE_JOIN_MITER)
    ctx.new_path()
    ctx.rectangle(crop[0], crop[1], crop_w, crop_h)          # black panel
    for r in range(ROWS):
        for c in range(COLS):
            ch = GRID[r][c]
            cx, cy = cell_center(r, c)
            x, y = glyph_xy(ctx, ref, ch, cx, cy)
            glyph_fix.append_path(ctx, ch, FONT_SIZE, x, y)   # letters -> holes
    for dx in dot_xs():
        ctx.new_sub_path()
        ctx.arc(dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)    # dots -> holes
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.fill()

    return crop_w, crop_h


def generate(pdf_path):
    surface = cairo.PDFSurface(pdf_path, A3_W * MM_TO_PT, A3_H * MM_TO_PT)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)
    crop_w, crop_h = draw(ctx)
    surface.finish()
    return crop_w, crop_h


if __name__ == "__main__":
    base = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru"
    pdf = f"{base}/print_a3.pdf"
    crop_w, crop_h = generate(pdf)
    shutil.copy2(pdf, f"/home/medivack/Downloads/{os.path.basename(pdf)}")
    print("A3 print PDF generated (print at 100% / actual size):")
    print(f"  PDF: {pdf}")
    print(f"  Page: A3 portrait {A3_W:.0f} x {A3_H:.0f} mm, 1:1")
    print(f"  Cropped face (5mm around outer letters): {crop_w:.1f} x {crop_h:.1f} mm")
    print("  Copied to ~/Downloads")
