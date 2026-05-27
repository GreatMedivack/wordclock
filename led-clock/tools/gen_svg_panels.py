#!/usr/bin/env python3
"""Regenerate panel_front.svg, baffle_grid.svg, cutting_template.svg with dot row."""

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
DOT_PAIR_SPACING = PITCH * 1.5
DOT_GAP = PITCH * 3
DOT_RADIUS = 3.0
NUM_DOTS = 4
PANEL_H = DOT_ROW_Y + DOT_RADIUS + MARGIN

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
    return round(x, 2), round(y, 2)


def dot_positions():
    cx = PANEL_W / 2
    return [
        (round(cx - DOT_GAP / 2 - DOT_PAIR_SPACING, 2), round(DOT_ROW_Y, 2)),
        (round(cx - DOT_GAP / 2, 2), round(DOT_ROW_Y, 2)),
        (round(cx + DOT_GAP / 2, 2), round(DOT_ROW_Y, 2)),
        (round(cx + DOT_GAP / 2 + DOT_PAIR_SPACING, 2), round(DOT_ROW_Y, 2)),
    ]


def led_index(row, col):
    if row % 2 == 0:
        return row * 16 + col
    else:
        return row * 16 + (15 - col)


def generate_panel_front():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}mm" height="{PANEL_H:.2f}mm" viewBox="0 0 {PANEL_W} {PANEL_H:.2f}">')
    lines.append(f'  <rect width="{PANEL_W}" height="{PANEL_H:.2f}" fill="#1a1a1a"/>')
    lines.append(f'  <rect x="0" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="none" stroke="red" stroke-width="0.2"/>')

    for r in range(ROWS + 1):
        y = MARGIN + r * PITCH
        lines.append(f'  <line x1="{MARGIN}" y1="{y}" x2="{PANEL_W - MARGIN}" y2="{y}" stroke="#333" stroke-width="0.1"/>')
    for c in range(COLS + 1):
        x = MARGIN + c * PITCH
        lines.append(f'  <line x1="{x}" y1="{MARGIN}" x2="{x}" y2="{GRID_BOTTOM}" stroke="#333" stroke-width="0.1"/>')

    font = 'font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="8"'
    anchor = 'text-anchor="middle" dominant-baseline="central"'
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            ch = GRID[r][c]
            fill = "white" if (r, c) in ACTIVE else "#555"
            lines.append(f'  <text x="{cx}" y="{cy}" {font} fill="{fill}" {anchor}>{ch}</text>')

    for dx, dy in dot_positions():
        lines.append(f'  <circle cx="{dx}" cy="{dy}" r="{DOT_RADIUS}" fill="white" stroke="#333" stroke-width="0.1"/>')

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_baffle_grid():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}mm" height="{PANEL_H:.2f}mm" viewBox="0 0 {PANEL_W} {PANEL_H:.2f}">')
    lines.append(f'  <rect width="{PANEL_W}" height="{PANEL_H:.2f}" fill="white"/>')
    lines.append(f'  <rect x="0" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="none" stroke="red" stroke-width="0.2"/>')

    for r in range(ROWS + 1):
        y = MARGIN + r * PITCH
        lines.append(f'  <line x1="{MARGIN}" y1="{y}" x2="{PANEL_W - MARGIN}" y2="{y}" stroke="blue" stroke-width="0.15"/>')
    for c in range(COLS + 1):
        x = MARGIN + c * PITCH
        lines.append(f'  <line x1="{x}" y1="{MARGIN}" x2="{x}" y2="{GRID_BOTTOM}" stroke="blue" stroke-width="0.15"/>')

    font = 'font-family="monospace" font-size="3.5" fill="#999"'
    anchor = 'text-anchor="middle" dominant-baseline="central"'
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            idx = led_index(r, c)
            lines.append(f'  <text x="{cx}" y="{cy}" {font} {anchor}>{idx}</text>')

    for i, (dx, dy) in enumerate(dot_positions()):
        idx = 256 + i
        lines.append(f'  <circle cx="{dx}" cy="{dy}" r="{DOT_RADIUS}" fill="none" stroke="blue" stroke-width="0.15"/>')
        lines.append(f'  <text x="{dx}" y="{dy}" {font} {anchor}>{idx}</text>')

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_cutting_template():
    GAP = 10.0
    TOTAL_W = PANEL_W * 2 + GAP
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}mm" height="{PANEL_H:.2f}mm" viewBox="0 0 {TOTAL_W} {PANEL_H:.2f}">')
    lines.append(f'  <rect width="{TOTAL_W}" height="{PANEL_H:.2f}" fill="#f5f5f5"/>')

    offsets = [0, PANEL_W + GAP]

    # Left panel: front view (dark, letters)
    ox = offsets[0]
    lines.append(f'  <rect x="{ox}" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="#1a1a1a"/>')
    lines.append(f'  <rect x="{ox}" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="none" stroke="red" stroke-width="0.2"/>')

    for r in range(ROWS + 1):
        y = MARGIN + r * PITCH
        lines.append(f'  <line x1="{ox + MARGIN}" y1="{y}" x2="{ox + PANEL_W - MARGIN}" y2="{y}" stroke="#333" stroke-width="0.1"/>')
    for c in range(COLS + 1):
        x = ox + MARGIN + c * PITCH
        lines.append(f'  <line x1="{x}" y1="{MARGIN}" x2="{x}" y2="{GRID_BOTTOM}" stroke="#333" stroke-width="0.1"/>')

    font = 'font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="8"'
    anchor = 'text-anchor="middle" dominant-baseline="central"'
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            ch = GRID[r][c]
            fill = "white" if (r, c) in ACTIVE else "#555"
            lines.append(f'  <text x="{ox + cx}" y="{cy}" {font} fill="{fill}" {anchor}>{ch}</text>')

    for dx, dy in dot_positions():
        lines.append(f'  <circle cx="{ox + dx}" cy="{dy}" r="{DOT_RADIUS}" fill="white" stroke="#333" stroke-width="0.1"/>')

    # Right panel: back view (white, LED indices)
    ox = offsets[1]
    lines.append(f'  <rect x="{ox}" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="white"/>')
    lines.append(f'  <rect x="{ox}" y="0" width="{PANEL_W}" height="{PANEL_H:.2f}" fill="none" stroke="red" stroke-width="0.2"/>')

    for r in range(ROWS + 1):
        y = MARGIN + r * PITCH
        lines.append(f'  <line x1="{ox + MARGIN}" y1="{y}" x2="{ox + PANEL_W - MARGIN}" y2="{y}" stroke="blue" stroke-width="0.15"/>')
    for c in range(COLS + 1):
        x = ox + MARGIN + c * PITCH
        lines.append(f'  <line x1="{x}" y1="{MARGIN}" x2="{x}" y2="{GRID_BOTTOM}" stroke="blue" stroke-width="0.15"/>')

    mono = 'font-family="monospace" font-size="3.5" fill="#999"'
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            idx = led_index(r, c)
            lines.append(f'  <text x="{ox + cx}" y="{cy}" {mono} {anchor}>{idx}</text>')

    for i, (dx, dy) in enumerate(dot_positions()):
        idx = 256 + i
        lines.append(f'  <circle cx="{ox + dx}" cy="{dy}" r="{DOT_RADIUS}" fill="none" stroke="blue" stroke-width="0.15"/>')
        lines.append(f'  <text x="{ox + dx}" y="{dy}" {mono} {anchor}>{idx}</text>')

    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == "__main__":
    base = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru"

    for name, gen in [("panel_front.svg", generate_panel_front),
                      ("baffle_grid.svg", generate_baffle_grid),
                      ("cutting_template.svg", generate_cutting_template)]:
        path = f"{base}/{name}"
        content = gen()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  {name}: {PANEL_W:.2f} × {PANEL_H:.2f} mm")

    print(f"\nAll SVGs updated with {NUM_DOTS} dot indicators below grid.")
