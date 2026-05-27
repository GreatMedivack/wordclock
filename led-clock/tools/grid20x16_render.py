#!/usr/bin/env python3
"""Render 20×16 word clock samples as PNG images."""

from PIL import Image, ImageDraw, ImageFont

GRID = [
    "ОДИНЖДВАКТРИБШПГ",
    "ЧЕТЫРЕЖПЯТЬКБШПГ",
    "ШЕСТЬЖСЕМЬКБШПГУ",
    "ВОСЕМЬЖДЕВЯТЬКБШ",
    "ДЕСЯТЬЖКБШПГУЦХР",
    "ОДИННАДЦАТЬЖКБШП",
    "ДВЕНАДЦАТЬЖКБШПГ",
    "ДВАДЦАТЬТРИДЦАТЬ",
    "СОРОКЖПЯТЬДЕСЯТК",
    "ДЕСЯТЬЖДЕВЯТЬКБШ",
    "ОДИННАДЦАТЬЖСЕМЬ",
    "ДВЕНАДЦАТЬЖШЕСТЬ",
    "ТРИНАДЦАТЬЖПЯТЬК",
    "ЧЕТЫРНАДЦАТЬЖТРИ",
    "ПЯТНАДЦАТЬЖДВЕКБ",
    "ШЕСТНАДЦАТЬЖОДНА",
    "СЕМНАДЦАТЬЖНОЛЬК",
    "ВОСЕМНАДЦАТЬЖКБШ",
    "ДЕВЯТНАДЦАТЬЖКБШ",
    "ВОСЕМЬЖЧЕТЫРЕКБШ",
]

COLS = 16
ROWS = 20

HOURS = {
    1:  (0, 0, 4),    2:  (0, 5, 8),    3:  (0, 9, 12),
    4:  (1, 0, 6),    5:  (1, 7, 11),   6:  (2, 0, 5),
    7:  (2, 6, 10),   8:  (3, 0, 6),    9:  (3, 7, 13),
    10: (4, 0, 6),    11: (5, 0, 11),   12: (6, 0, 10),
}

TEENS = {
    10: (9, 0, 6),     11: (10, 0, 11),  12: (11, 0, 10),
    13: (12, 0, 10),   14: (13, 0, 12),  15: (14, 0, 10),
    16: (15, 0, 11),   17: (16, 0, 10),  18: (17, 0, 12),
    19: (18, 0, 12),
}

TENS = {
    20: (7, 0, 8),   30: (7, 8, 16),
    40: (8, 0, 5),   50: (8, 6, 15),
}

UNITS = {
    0: (16, 11, 15),   1: (15, 12, 16),  2: (14, 11, 14),
    3: (13, 13, 16),   4: (19, 7, 13),   5: (12, 11, 15),
    6: (11, 11, 16),   7: (10, 12, 16),  8: (19, 0, 6),
    9: (9, 7, 13),
}


def active_positions(hour12, minute):
    active = set()
    row, cs, ce = HOURS[hour12]
    for c in range(cs, ce):
        active.add((row, c))
    if minute == 0:
        return active
    if 1 <= minute <= 9:
        for r, cs, ce in [UNITS[0], UNITS[minute]]:
            for c in range(cs, ce):
                active.add((r, c))
    elif 10 <= minute <= 19:
        row, cs, ce = TEENS[minute]
        for c in range(cs, ce):
            active.add((row, c))
    else:
        tens_val = (minute // 10) * 10
        ones_val = minute % 10
        row, cs, ce = TENS[tens_val]
        for c in range(cs, ce):
            active.add((row, c))
        if ones_val > 0:
            row, cs, ce = UNITS[ones_val]
            for c in range(cs, ce):
                active.add((row, c))
    return active


def describe(h, m):
    hn = {1:"ОДИН",2:"ДВА",3:"ТРИ",4:"ЧЕТЫРЕ",5:"ПЯТЬ",6:"ШЕСТЬ",
          7:"СЕМЬ",8:"ВОСЕМЬ",9:"ДЕВЯТЬ",10:"ДЕСЯТЬ",11:"ОДИННАДЦАТЬ",12:"ДВЕНАДЦАТЬ"}
    tn = {10:"ДЕСЯТЬ",11:"ОДИННАДЦАТЬ",12:"ДВЕНАДЦАТЬ",13:"ТРИНАДЦАТЬ",
          14:"ЧЕТЫРНАДЦАТЬ",15:"ПЯТНАДЦАТЬ",16:"ШЕСТНАДЦАТЬ",17:"СЕМНАДЦАТЬ",
          18:"ВОСЕМНАДЦАТЬ",19:"ДЕВЯТНАДЦАТЬ"}
    un = {0:"НОЛЬ",1:"ОДНА",2:"ДВЕ",3:"ТРИ",4:"ЧЕТЫРЕ",5:"ПЯТЬ",
          6:"ШЕСТЬ",7:"СЕМЬ",8:"ВОСЕМЬ",9:"ДЕВЯТЬ"}
    tns = {20:"ДВАДЦАТЬ",30:"ТРИДЦАТЬ",40:"СОРОК",50:"ПЯТЬДЕСЯТ"}
    parts = [hn[h]]
    if m == 0: pass
    elif 1 <= m <= 9: parts += ["НОЛЬ", un[m]]
    elif 10 <= m <= 19: parts.append(tn[m])
    else:
        parts.append(tns[(m//10)*10])
        if m % 10: parts.append(un[m%10])
    return " ".join(parts)


CELL = 40
PAD = 5
FONT_SIZE = 20
TITLE_SIZE = 18

BG_COLOR = (20, 20, 25)
DIM_COLOR = (55, 55, 65)
ON_COLOR = (255, 200, 100)
TITLE_COLOR = (200, 200, 210)

CLOCK_W = COLS * CELL + PAD * 2
CLOCK_H = ROWS * CELL + PAD * 2
LABEL_H = 36

try:
    font = ImageFont.truetype("/usr/share/fonts/liberation-mono/LiberationMono-Bold.ttf", FONT_SIZE)
except:
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", FONT_SIZE)
    except:
        font = ImageFont.truetype("fonts/LiberationMono-Bold.ttf", FONT_SIZE)

try:
    title_font = ImageFont.truetype("/usr/share/fonts/liberation-mono/LiberationMono-Bold.ttf", TITLE_SIZE)
except:
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", TITLE_SIZE)
    except:
        title_font = ImageFont.truetype("fonts/LiberationMono-Bold.ttf", TITLE_SIZE)


def render_one(h, m):
    active = active_positions(h, m)
    w = CLOCK_W
    total_h = LABEL_H + CLOCK_H
    img = Image.new("RGB", (w, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    label = f"{h}:{m:02d} — {describe(h, m)}"
    bbox = title_font.getbbox(label)
    lw = bbox[2] - bbox[0]
    draw.text(((w - lw) // 2, 8), label, font=title_font, fill=TITLE_COLOR)

    oy = LABEL_H
    for ri, row_text in enumerate(GRID):
        for ci, ch in enumerate(row_text):
            cx = PAD + ci * CELL
            cy = oy + PAD + ri * CELL

            color = ON_COLOR if (ri, ci) in active else DIM_COLOR

            bbox = font.getbbox(ch)
            gw = bbox[2] - bbox[0]
            gh = bbox[3] - bbox[1]
            tx = cx + (CELL - gw) // 2
            ty = cy + (CELL - gh) // 2 - bbox[1]
            draw.text((tx, ty), ch, font=font, fill=color)

    return img


SAMPLES = [
    (12, 0),  (1, 0),   (7, 1),   (3, 5),   (5, 9),
    (8, 10),  (11, 11), (2, 15),  (6, 17),  (4, 19),
    (9, 20),  (7, 21),  (10, 25), (12, 30), (1, 33),
    (3, 40),  (8, 42),  (5, 50),  (11, 55), (6, 59),
]

# 4 columns × 5 rows
GRID_COLS = 4
GRID_ROWS = 5
GAP = 10

one = render_one(12, 0)
tile_w, tile_h = one.size

total_w = GRID_COLS * tile_w + (GRID_COLS + 1) * GAP
total_h = GRID_ROWS * tile_h + (GRID_ROWS + 1) * GAP

sheet = Image.new("RGB", (total_w, total_h), (10, 10, 12))

for idx, (h, m) in enumerate(SAMPLES):
    col = idx % GRID_COLS
    row = idx // GRID_COLS
    tile = render_one(h, m)
    x = GAP + col * (tile_w + GAP)
    y = GAP + row * (tile_h + GAP)
    sheet.paste(tile, (x, y))

out = "/home/medivack/Downloads/wordclock_20x16_samples.png"
sheet.save(out)
print(f"Saved: {out}  ({total_w}×{total_h}px)")
