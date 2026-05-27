#!/usr/bin/env python3
"""Regenerate panel_front.svg, baffle_grid.svg, cutting_template.svg with dot row.

Uses Cairo to convert text to paths so USSR STENCIL font is embedded.
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
PITCH = 16.67
MARGIN = 5.0
PANEL_W = MARGIN * 2 + PITCH * COLS
GRID_BOTTOM = MARGIN + PITCH * ROWS
DOT_ROW_Y = GRID_BOTTOM + 20.0
DOT_RADIUS = 5.0
NUM_DOTS = 4
PANEL_H = DOT_ROW_Y + DOT_RADIUS + MARGIN

FONT_FACE = "USSR STENCIL"
FONT_SIZE = 17.6
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
    return MARGIN + (col + 0.5) * PITCH, MARGIN + (row + 0.5) * PITCH


def dot_xs():
    return [
        cell_center(0, 5)[0],
        cell_center(0, 6)[0],
        cell_center(0, 9)[0],
        cell_center(0, 10)[0],
    ]


def led_index(row, col):
    if row % 2 == 0:
        return row * 16 + col
    else:
        return row * 16 + (15 - col)


def _draw_grid_lines(ctx, ox=0):
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.set_line_width(0.1)
    for r in range(ROWS + 1):
        y = MARGIN + r * PITCH
        ctx.move_to(ox + MARGIN, y)
        ctx.line_to(ox + PANEL_W - MARGIN, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = ox + MARGIN + c * PITCH
        ctx.move_to(x, MARGIN)
        ctx.line_to(x, GRID_BOTTOM)
        ctx.stroke()


def _draw_text_centered(ctx, cx, cy, ch):
    ext = ctx.text_extents(ch)
    x = cx - ext.width / 2 - ext.x_bearing
    y = cy - ext.height / 2 - ext.y_bearing
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
            _draw_text_centered(ctx, cx, cy, GRID[r][c])
            if (r, c) in ACTIVE:
                ctx.set_source_rgb(1, 1, 1)
            else:
                ctx.set_source_rgb(0.33, 0.33, 0.33)
            ctx.fill()

    for dx in dot_xs():
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
        y = MARGIN + r * PITCH
        ctx.move_to(MARGIN, y)
        ctx.line_to(PANEL_W - MARGIN, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = MARGIN + c * PITCH
        ctx.move_to(x, MARGIN)
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
            _draw_text_centered(ctx, ox + cx, cy, GRID[r][c])
            if (r, c) in ACTIVE:
                ctx.set_source_rgb(1, 1, 1)
            else:
                ctx.set_source_rgb(0.33, 0.33, 0.33)
            ctx.fill()

    for dx in dot_xs():
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
        y = MARGIN + r * PITCH
        ctx.move_to(ox + MARGIN, y)
        ctx.line_to(ox + PANEL_W - MARGIN, y)
        ctx.stroke()
    for c in range(COLS + 1):
        x = ox + MARGIN + c * PITCH
        ctx.move_to(x, MARGIN)
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

    print(f"\nAll SVGs updated with {NUM_DOTS} dot indicators below grid.")
