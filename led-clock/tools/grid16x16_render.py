#!/usr/bin/env python3
"""Render 16×16 natural speech word clock samples with corner dots."""

from PIL import Image, ImageDraw, ImageFont

GRID = [
    "ГДВАДЦАТЬГПЯТЬГЖ",  #  0: ДВАДЦАТЬ _ ПЯТЬ_M
    "ЖГДЕСЯТЬГМИНУТГЖ",  #  1: ДЕСЯТЬ_M _ МИНУТ
    "ЧЕТВЕРТЬПОЛОВИНА",  #  2: ЧЕТВЕРТЬ ПОЛОВИНА
    "ГБЕЗГДВАДЦАТИГЖГ",  #  3: БЕЗ _ ДВАДЦАТИ
    "ПЯТИГЧЕТВЕРТИГГГ",  #  4: ПЯТИ _ ЧЕТВЕРТИ
    "ДЕСЯТИПЕРВОГОТРИ",  #  5: ДЕСЯТИ ПЕРВОГО ТРИ
    "ВТОРОГОПЯТОГОЧАС",  #  6: ВТОРОГО ПЯТОГО ЧАС
    "ТРЕТЬЕГОШЕСТОГОГ",  #  7: ТРЕТЬЕГО ШЕСТОГО
    "ЧЕТВЁРТОГОЧЕТЫРЕ",  #  8: ЧЕТВЁРТОГО ЧЕТЫРЕ
    "СЕДЬМОГОВОСЬМОГО",  #  9: СЕДЬМОГО ВОСЬМОГО
    "ДЕВЯТОГОДЕСЯТОГО",  # 10: ДЕВЯТОГО ДЕСЯТОГО
    "ОДИННАДЦАТОГОДВА",  # 11: ОДИННАДЦАТОГО ДВА
    "ДВЕНАДЦАТОГОПЯТЬ",  # 12: ДВЕНАДЦАТОГО ПЯТЬ
    "ДВЕНАДЦАТЬДЕСЯТЬ",  # 13: ДВЕНАДЦАТЬ ДЕСЯТЬ
    "ОДИННАДЦАТЬШЕСТЬ",  # 14: ОДИННАДЦАТЬ ШЕСТЬ
    "СЕМЬВОСЕМЬДЕВЯТЬ",  # 15: СЕМЬ ВОСЕМЬ ДЕВЯТЬ
]
# + 4 dot LEDs (256-259) below grid

COLS = 16
ROWS = 16

# Minute/modifier words
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
        add_word(active, W_PYAT_M)
        add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 10:
        add_word(active, W_DESYAT_M)
        add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 15:
        add_word(active, W_CHETVERT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 20:
        add_word(active, W_DVADTSAT)
        add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 25:
        add_word(active, W_DVADTSAT)
        add_word(active, W_PYAT_M)
        add_word(active, W_MINUT)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 30:
        add_word(active, W_POLOVINA)
        add_word(active, HOURS_GEN[nh])
    elif m5 == 35:
        add_word(active, W_BEZ)
        add_word(active, W_DVADTSATI)
        add_word(active, W_PYATI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 40:
        add_word(active, W_BEZ)
        add_word(active, W_DVADTSATI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 45:
        add_word(active, W_BEZ)
        add_word(active, W_CHETVERTI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 50:
        add_word(active, W_BEZ)
        add_word(active, W_DESYATI)
        add_word(active, HOURS_NOM[nh])
    elif m5 == 55:
        add_word(active, W_BEZ)
        add_word(active, W_PYATI)
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


CELL = 52
PAD = 8
FONT_SIZE = 57
TITLE_SIZE = 24
DOT_R = 16

BG_COLOR = (15, 15, 18)
DIM_COLOR = (45, 45, 55)
ON_COLOR = (255, 190, 80)
TITLE_COLOR = (180, 180, 195)
DOT_COLOR = (255, 190, 80)

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(script_dir, os.pardir, "arduino", "wordclock_ru", "USSRStencil.ttf")
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
title_font = ImageFont.truetype(FONT_PATH, TITLE_SIZE)

CLOCK_W = COLS * CELL + PAD * 2
CLOCK_H = ROWS * CELL + PAD * 2
DOT_ROW_H = CELL + PAD
TITLE_H = 48


MINUS_COLOR = (255, 120, 80)

def render_one(h, m):
    active, plus_dots, minus_dots = active_positions(h, m)
    total_h = TITLE_H + CLOCK_H + DOT_ROW_H
    img = Image.new("RGB", (CLOCK_W, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    label = f"{h}:{m:02d} — {describe(h, m)}"
    bbox = title_font.getbbox(label)
    lw = bbox[2] - bbox[0]
    tx = max(6, (CLOCK_W - lw) // 2)
    draw.text((tx, 12), label, font=title_font, fill=ON_COLOR)

    oy = TITLE_H
    for ri, row_text in enumerate(GRID):
        for ci, ch in enumerate(row_text):
            cx = PAD + ci * CELL
            cy = oy + PAD + ri * CELL
            color = ON_COLOR if (ri, ci) in active else DIM_COLOR
            bbox = font.getbbox(ch)
            gw = bbox[2] - bbox[0]
            gh = bbox[3] - bbox[1]
            ftx = cx + (CELL - gw) // 2
            fty = cy + (CELL - gh) // 2 - bbox[1]
            draw.text((ftx, fty), ch, font=font, fill=color)

    # Dot row: ●● [gap] ●● — left pair = minus, right pair = plus
    dot_y = oy + CLOCK_H + DOT_ROW_H // 2

    dot_positions = [
        PAD + 6 * CELL + CELL // 2,
        PAD + 7 * CELL + CELL // 2,
        PAD + 10 * CELL + CELL // 2,
        PAD + 11 * CELL + CELL // 2,
    ]

    for i, dx in enumerate(dot_positions):
        if i < 2:
            filled = (2 - i) <= minus_dots
            color = MINUS_COLOR if filled else DIM_COLOR
        else:
            filled = (i - 1) <= plus_dots
            color = DOT_COLOR if filled else DIM_COLOR
        draw.ellipse([dx - DOT_R, dot_y - DOT_R, dx + DOT_R, dot_y + DOT_R], fill=color)

    return img


SAMPLES = [
    (12, 0),   (7, 1),    (3, 2),    (5, 3),
    (8, 5),    (2, 7),    (11, 8),   (6, 10),
    (1, 11),   (9, 12),   (4, 13),   (10, 15),
    (6, 16),   (1, 17),   (12, 18),  (3, 20),
    (7, 21),   (5, 22),   (8, 23),   (11, 25),
    (9, 26),   (4, 27),   (2, 28),   (10, 30),
    (12, 31),  (6, 32),   (1, 33),   (7, 35),
    (3, 36),   (5, 37),   (8, 38),   (11, 40),
    (2, 41),   (9, 42),   (4, 43),   (10, 45),
    (12, 46),  (6, 47),   (1, 48),   (7, 50),
    (3, 51),   (5, 52),   (8, 53),   (11, 55),
    (2, 57),   (9, 58),   (4, 59),   (12, 58),
]

GAP = 16
tile = render_one(12, 0)
tw, th = tile.size
cols_n = 4
per_page = 20
pages = (len(SAMPLES) + per_page - 1) // per_page

for page in range(pages):
    page_samples = SAMPLES[page*per_page : (page+1)*per_page]
    rows_n = (len(page_samples) + cols_n - 1) // cols_n
    pw = cols_n * tw + (cols_n + 1) * GAP
    ph = rows_n * th + (rows_n + 1) * GAP
    sheet = Image.new("RGB", (pw, ph), (8, 8, 10))
    for idx, (h, m) in enumerate(page_samples):
        col = idx % cols_n
        row = idx // cols_n
        tile = render_one(h, m)
        x = GAP + col * (tw + GAP)
        y = GAP + row * (th + GAP)
        sheet.paste(tile, (x, y))
    out = f"/home/medivack/Downloads/wordclock_16x16_page{page+1}.png"
    sheet.save(out)
    print(f"Page {page+1}: {out}  ({pw}×{ph}px)")
