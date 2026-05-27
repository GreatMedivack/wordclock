#!/usr/bin/env python3
"""Generate animated GIF: full 12-hour word clock demo, 2s per frame."""

import os
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


def describe(h, m):
    remainder = m % 5
    if remainder <= 2:
        m5 = (m // 5) * 5
        plus_dots = remainder
        minus_dots = 0
    else:
        m5 = (m // 5) * 5 + 5
        minus_dots = 5 - remainder
        plus_dots = 0

    hr = h
    if m5 == 60:
        m5 = 0
        hr = next_hour(hr)
    nh = next_hour(hr)

    gn = {1:"ПЕРВОГО",2:"ВТОРОГО",3:"ТРЕТЬЕГО",4:"ЧЕТВЁРТОГО",5:"ПЯТОГО",
          6:"ШЕСТОГО",7:"СЕДЬМОГО",8:"ВОСЬМОГО",9:"ДЕВЯТОГО",10:"ДЕСЯТОГО",
          11:"ОДИННАДЦАТОГО",12:"ДВЕНАДЦАТОГО"}
    nm = {1:"ЧАС",2:"ДВА",3:"ТРИ",4:"ЧЕТЫРЕ",5:"ПЯТЬ",6:"ШЕСТЬ",
          7:"СЕМЬ",8:"ВОСЕМЬ",9:"ДЕВЯТЬ",10:"ДЕСЯТЬ",11:"ОДИННАДЦАТЬ",12:"ДВЕНАДЦАТЬ"}

    phrases = {
        0: nm[hr],
        5: f"ПЯТЬ МИНУТ {gn[nh]}",
        10: f"ДЕСЯТЬ МИНУТ {gn[nh]}",
        15: f"ЧЕТВЕРТЬ {gn[nh]}",
        20: f"ДВАДЦАТЬ МИНУТ {gn[nh]}",
        25: f"ДВАДЦАТЬ ПЯТЬ МИНУТ {gn[nh]}",
        30: f"ПОЛОВИНА {gn[nh]}",
        35: f"БЕЗ ДВАДЦАТИ ПЯТИ {nm[nh]}",
        40: f"БЕЗ ДВАДЦАТИ {nm[nh]}",
        45: f"БЕЗ ЧЕТВЕРТИ {nm[nh]}",
        50: f"БЕЗ ДЕСЯТИ {nm[nh]}",
        55: f"БЕЗ ПЯТИ {nm[nh]}",
    }
    text = phrases[m5]
    if minus_dots:
        text += " −" + "●" * minus_dots
    if plus_dots:
        text += " +" + "●" * plus_dots
    return text


CELL = 40
PAD = 6
FONT_SIZE = 44
LABEL_SIZE = 16
DOT_R = 6

BG = (12, 12, 15)
DIM = (35, 35, 42)
ON = (255, 180, 60)
MINUS_CLR = (255, 120, 70)
LABEL_CLR = (140, 140, 155)

CLOCK_W = COLS * CELL + PAD * 2
CLOCK_H = ROWS * CELL + PAD * 2
DOT_ROW_H = CELL
LABEL_H = 36
IMG_W = CLOCK_W
IMG_H = LABEL_H + CLOCK_H + DOT_ROW_H

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))

FONT_PATH = os.path.join(script_dir, os.pardir, "arduino", "wordclock_ru", "USSRStencil.ttf")
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
label_font = ImageFont.truetype(FONT_PATH, LABEL_SIZE)


def render_frame(hour12, minute):
    active, plus_dots, minus_dots = active_positions(hour12, minute)
    img = Image.new("RGB", (IMG_W, IMG_H), BG)
    draw = ImageDraw.Draw(img)

    label = f"{hour12}:{minute:02d}  {describe(hour12, minute)}"
    bbox = label_font.getbbox(label)
    lw = bbox[2] - bbox[0]
    tx = max(PAD, (IMG_W - lw) // 2)
    draw.text((tx, 10), label, font=label_font, fill=LABEL_CLR)

    oy = LABEL_H
    for ri, row_text in enumerate(GRID):
        for ci, ch in enumerate(row_text):
            cx = PAD + ci * CELL
            cy = oy + PAD + ri * CELL
            color = ON if (ri, ci) in active else DIM
            bbox = font.getbbox(ch)
            gw = bbox[2] - bbox[0]
            gh = bbox[3] - bbox[1]
            ftx = cx + (CELL - gw) // 2
            fty = cy + (CELL - gh) // 2 - bbox[1]
            draw.text((ftx, fty), ch, font=font, fill=color)

    dot_y = oy + CLOCK_H + DOT_ROW_H // 2
    gap = CELL
    pair_sp = DOT_R * 2 + CELL // 3
    center_x = IMG_W // 2

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


if __name__ == "__main__":
    out_dir = os.path.join(script_dir, os.pardir)
    out_path = os.path.normpath(os.path.join(out_dir, "wordclock_12h_demo.gif"))

    frames = []
    for h12 in range(1, 13):
        for minute in range(60):
            frames.append(render_frame(h12, minute))
            print(f"\r  rendering {h12}:{minute:02d}  ({len(frames)}/720)", end="", flush=True)

    print(f"\n  saving {len(frames)} frames to {out_path} ...")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=2000,
        loop=0,
    )
    print(f"Done: {out_path}  ({IMG_W}×{IMG_H}px, {len(frames)} frames, 2s/frame)")
