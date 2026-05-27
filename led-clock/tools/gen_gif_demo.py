#!/usr/bin/env python3
"""Generate animated GIF: word clock 13:00–14:00 with warm letter highlights."""

from PIL import Image, ImageDraw, ImageFont

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

W_DVADTSAT  = (0,  1,  9)
W_PYAT_M    = (0, 10, 14)
W_DESYAT_M  = (1,  2,  8)
W_MINUT     = (1,  9, 14)
W_CHETVERT  = (2,  0,  8)
W_POLOVINA  = (2,  8, 16)
W_BEZ       = (3,  1,  4)
W_DVADTSATI = (3,  5, 13)
W_PYATI     = (4,  0,  4)
W_DESYATI   = (5,  0,  6)
W_CHETVERTI = (4,  5, 13)

HOURS_GEN = {
    1:  (5,   6, 13),  2:  (6,   0,  7),  3:  (7,   0,  8),
    4:  (8,   0, 10),  5:  (6,   7, 13),  6:  (7,   8, 15),
    7:  (9,   0,  8),  8:  (9,   8, 16),  9:  (10,  0,  8),
    10: (10,  8, 16),  11: (11,  0, 13),  12: (12,  0, 12),
}

HOURS_NOM = {
    1:  (6,  13, 16),  2:  (11, 13, 16),  3:  (5,  13, 16),
    4:  (8,  10, 16),  5:  (12, 12, 16),  6:  (14, 11, 16),
    7:  (15,  0,  4),  8:  (15,  4, 10),  9:  (15, 10, 16),
    10: (13, 10, 16),  11: (14,  0, 11),  12: (13,  0, 10),
}


def next_hour(h):
    return h % 12 + 1


def add_word(active, word):
    r, cs, ce = word
    for c in range(cs, ce):
        active.add((r, c))


def active_positions(hour12, minute):
    active = set()
    remainder = minute % 5
    if remainder <= 2:
        m5 = (minute // 5) * 5
        plus_dots = remainder
        minus_dots = 0
    else:
        m5 = (minute // 5) * 5 + 5
        minus_dots = 5 - remainder
        plus_dots = 0

    h = hour12
    if m5 == 60:
        m5 = 0
        h = next_hour(h)
    nh = next_hour(h)

    if m5 == 0:
        add_word(active, HOURS_NOM[h])
    elif m5 == 5:
        add_word(active, W_PYAT_M); add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 10:
        add_word(active, W_DESYAT_M); add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 15:
        add_word(active, W_CHETVERT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 20:
        add_word(active, W_DVADTSAT); add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 25:
        add_word(active, W_DVADTSAT); add_word(active, W_PYAT_M)
        add_word(active, W_MINUT); add_word(active, HOURS_GEN[nh])
    elif m5 == 30:
        add_word(active, W_POLOVINA)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 35:
        add_word(active, W_BEZ); add_word(active, W_DVADTSATI)
        add_word(active, W_PYATI); add_word(active, HOURS_NOM[nh])
    elif m5 == 40:
        add_word(active, W_BEZ); add_word(active, W_DVADTSATI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 45:
        add_word(active, W_BEZ); add_word(active, W_CHETVERTI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 50:
        add_word(active, W_BEZ); add_word(active, W_DESYATI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 55:
        add_word(active, W_BEZ); add_word(active, W_PYATI)
        add_word(active, HOURS_NOM[nh])

    return active, plus_dots, minus_dots


CELL = 40
PAD = 6
FONT_SIZE = 22
DOT_R = 6

BG = (12, 12, 15)
DIM = (35, 35, 42)
ON = (255, 180, 60)
MINUS_CLR = (255, 120, 70)

CLOCK_W = COLS * CELL + PAD * 2
CLOCK_H = ROWS * CELL + PAD * 2
DOT_ROW_H = CELL
IMG_H = CLOCK_H + DOT_ROW_H

font_paths = [
    "/usr/share/fonts/liberation-mono/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "fonts/LiberationMono-Bold.ttf",
]
font = None
for p in font_paths:
    try:
        font = ImageFont.truetype(p, FONT_SIZE)
        break
    except Exception:
        continue


def render_frame(hour12, minute):
    active, plus_dots, minus_dots = active_positions(hour12, minute)
    img = Image.new("RGB", (CLOCK_W, IMG_H), BG)
    draw = ImageDraw.Draw(img)

    for ri, row_text in enumerate(GRID):
        for ci, ch in enumerate(row_text):
            cx = PAD + ci * CELL
            cy = PAD + ri * CELL
            color = ON if (ri, ci) in active else DIM
            bbox = font.getbbox(ch)
            gw = bbox[2] - bbox[0]
            gh = bbox[3] - bbox[1]
            tx = cx + (CELL - gw) // 2
            ty = cy + (CELL - gh) // 2 - bbox[1]
            draw.text((tx, ty), ch, font=font, fill=color)

    dot_y = CLOCK_H + DOT_ROW_H // 2
    gap = CELL
    pair_sp = DOT_R * 2 + CELL // 3
    center_x = CLOCK_W // 2

    dot_positions = [
        center_x - gap - pair_sp - DOT_R,
        center_x - gap - DOT_R,
        center_x + gap + DOT_R,
        center_x + gap + pair_sp + DOT_R,
    ]

    for i, dx in enumerate(dot_positions):
        if i < 2:
            filled = (2 - i) <= minus_dots
            color = MINUS_CLR if filled else DIM
        else:
            filled = (i - 1) <= plus_dots
            color = ON if filled else DIM
        draw.ellipse([dx - DOT_R, dot_y - DOT_R, dx + DOT_R, dot_y + DOT_R], fill=color)

    return img


frames_1h = []
for minute in range(60):
    h12 = 1
    frames_1h.append(render_frame(h12, minute))
frames_1h.append(render_frame(2, 0))

out_1h = "/home/medivack/Downloads/wordclock_13_14.gif"
frames_1h[0].save(
    out_1h,
    save_all=True,
    append_images=frames_1h[1:],
    duration=500,
    loop=0,
)
print(f"Done: {out_1h}  ({CLOCK_W}×{IMG_H}px, {len(frames_1h)} frames)")

frames_12h = []
for h12 in range(1, 13):
    for minute in range(60):
        frames_12h.append(render_frame(h12, minute))
frames_12h.append(render_frame(1, 0))

out_12h = "/home/medivack/Downloads/wordclock_12h.gif"
frames_12h[0].save(
    out_12h,
    save_all=True,
    append_images=frames_12h[1:],
    duration=450,
    loop=0,
)
print(f"Done: {out_12h}  ({CLOCK_W}×{IMG_H}px, {len(frames_12h)} frames)")
