#!/usr/bin/env python3
"""Render 16×17 word clock with 'И МИНУТА/ДВЕ/ТРИ/ЧЕТЫРЕ МИНУТЫ' rows."""

from PIL import Image, ImageDraw, ImageFont

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
    "ОДИННАДЦАТЬМИНУТ",
    "ИЧЕТЫРЕАДВЕЖТРИЫ",
]

COLS = 16
ROWS = 17

W_DVADTSAT  = (0,  2, 10)
W_PYAT_M    = (0, 10, 14)
W_DESYAT_M  = (1,  3,  9)
W_MINUT     = (1,  9, 14)
W_CHETVERT  = (2,  0,  8)
W_POLOVINA  = (2,  8, 16)
W_BEZ       = (3,  2,  5)
W_PYATI     = (3,  5,  9)
W_DESYATI   = (3,  9, 15)
W_DVADTSATI = (4,  0,  8)
W_CHETVERTI = (4,  8, 16)

HOURS_GEN = {
    1:  (5,  1,  8),   2:  (5,  8, 15),   3:  (6,  0,  8),
    4:  (7,  0, 10),   5:  (7, 10, 16),   6:  (8,  0,  7),
    7:  (8,  7, 15),   8:  (9,  0,  8),   9:  (9,  8, 16),
    10: (6,  8, 16),   11: (10,  2, 15),  12: (11,  2, 14),
}

HOURS_NOM = {
    1:  (12,  0,  3),   2:  (12,  3,  6),   3:  (12,  6,  9),
    4:  (12,  9, 15),   5:  (0,  10, 14),   6:  (13,  0,  5),
    7:  (13,  5,  9),   8:  (13,  9, 15),   9:  (14,  0,  6),
    10: (1,   3,  9),   11: (15,  0, 11),   12: (14,  6, 16),
}

# Extra minute words
W_I       = (16, 0, 1)     # И
W_CHETYREM = (16, 1, 7)    # ЧЕТЫРЕ
W_A       = (16, 7, 8)     # А (for МИНУТА)
W_DVE     = (16, 8, 11)    # ДВЕ
W_TRI     = (16, 12, 15)   # ТРИ
W_Y       = (16, 15, 16)   # Ы (for МИНУТЫ)
W_MINUT2  = (15, 11, 16)   # МИНУТ (shared stem)


def next_hour(h):
    return h % 12 + 1


def add_word(active, word):
    r, cs, ce = word
    for c in range(cs, ce):
        active.add((r, c))


def active_positions(hour12, minute):
    active = set()
    m5 = (minute // 5) * 5
    extra = minute % 5
    h = hour12
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

    if extra == 1:
        add_word(active, W_I)
        add_word(active, W_MINUT2)  # МИНУТ
        add_word(active, W_A)       # +А = МИНУТА
    elif extra == 2:
        add_word(active, W_I)
        add_word(active, W_DVE)
        add_word(active, W_MINUT2)
        add_word(active, W_Y)       # +Ы = МИНУТЫ
    elif extra == 3:
        add_word(active, W_I)
        add_word(active, W_TRI)
        add_word(active, W_MINUT2)
        add_word(active, W_Y)
    elif extra == 4:
        add_word(active, W_I)
        add_word(active, W_CHETYREM)
        add_word(active, W_MINUT2)
        add_word(active, W_Y)

    return active, extra


def describe(h, m):
    m5 = (m // 5) * 5
    extra = m % 5
    nh = next_hour(h)

    gn = {1:"ПЕРВОГО",2:"ВТОРОГО",3:"ТРЕТЬЕГО",4:"ЧЕТВЁРТОГО",5:"ПЯТОГО",
          6:"ШЕСТОГО",7:"СЕДЬМОГО",8:"ВОСЬМОГО",9:"ДЕВЯТОГО",10:"ДЕСЯТОГО",
          11:"ОДИННАДЦАТОГО",12:"ДВЕНАДЦАТОГО"}
    nm = {1:"ЧАС",2:"ДВА",3:"ТРИ",4:"ЧЕТЫРЕ",5:"ПЯТЬ",6:"ШЕСТЬ",
          7:"СЕМЬ",8:"ВОСЕМЬ",9:"ДЕВЯТЬ",10:"ДЕСЯТЬ",11:"ОДИННАДЦАТЬ",12:"ДВЕНАДЦАТЬ"}

    phrases = {
        0: nm[h], 5: f"ПЯТЬ МИНУТ {gn[nh]}", 10: f"ДЕСЯТЬ МИНУТ {gn[nh]}",
        15: f"ЧЕТВЕРТЬ {gn[nh]}", 20: f"ДВАДЦАТЬ МИНУТ {gn[nh]}",
        25: f"ДВАДЦАТЬ ПЯТЬ МИНУТ {gn[nh]}", 30: f"ПОЛОВИНА {gn[nh]}",
        35: f"БЕЗ ДВАДЦАТИ ПЯТИ {nm[nh]}", 40: f"БЕЗ ДВАДЦАТИ {nm[nh]}",
        45: f"БЕЗ ЧЕТВЕРТИ {nm[nh]}", 50: f"БЕЗ ДЕСЯТИ {nm[nh]}",
        55: f"БЕЗ ПЯТИ {nm[nh]}",
    }
    text = phrases[m5]
    extras = {1: " И МИНУТА", 2: " И ДВЕ МИНУТЫ", 3: " И ТРИ МИНУТЫ", 4: " И ЧЕТЫРЕ МИНУТЫ"}
    if extra:
        text += extras[extra]
    return text


CELL = 52
PAD = 8
FONT_SIZE = 28
TITLE_SIZE = 20

BG_COLOR = (15, 15, 18)
DIM_COLOR = (45, 45, 55)
ON_COLOR = (255, 190, 80)

font_paths = [
    "/usr/share/fonts/liberation-mono/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "fonts/LiberationMono-Bold.ttf",
]
for p in font_paths:
    try:
        font = ImageFont.truetype(p, FONT_SIZE)
        title_font = ImageFont.truetype(p, TITLE_SIZE)
        break
    except:
        continue

CLOCK_W = COLS * CELL + PAD * 2
CLOCK_H = ROWS * CELL + PAD * 2
TITLE_H = 48


def render_one(h, m):
    active, _ = active_positions(h, m)
    img = Image.new("RGB", (CLOCK_W, TITLE_H + CLOCK_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    label = f"{h}:{m:02d} — {describe(h, m)}"
    bbox = title_font.getbbox(label)
    lw = bbox[2] - bbox[0]
    tx = max(6, (CLOCK_W - lw) // 2)
    draw.text((tx, 14), label, font=title_font, fill=ON_COLOR)

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

    return img


# All samples with extra minutes, covering every 5-min base + all 4 extras
SAMPLES = [
    (12, 1),   (7, 2),    (3, 3),    (5, 4),
    (8, 6),    (2, 7),    (11, 8),   (6, 9),
    (1, 11),   (9, 12),   (4, 13),   (10, 14),
    (6, 16),   (1, 17),   (12, 18),  (3, 19),
    (7, 21),   (5, 22),   (8, 23),   (11, 24),
    (9, 26),   (4, 27),   (2, 28),   (10, 29),
    (12, 31),  (6, 32),   (1, 33),   (7, 34),
    (3, 36),   (5, 37),   (8, 38),   (11, 39),
    (2, 41),   (9, 42),   (4, 43),   (10, 44),
    (12, 46),  (6, 47),   (1, 48),   (7, 49),
    (3, 51),   (5, 52),   (8, 53),   (11, 54),
    (2, 56),   (9, 57),   (4, 58),   (6, 59),
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
    out = f"/home/medivack/Downloads/wordclock_17x16_page{page+1}.png"
    sheet.save(out)
    print(f"Page {page+1}: {out}  ({pw}×{ph}px)")
