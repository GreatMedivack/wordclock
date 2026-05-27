import os
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 122
EPD_HEIGHT = 250

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "LiberationMono-Bold.ttf")
FONT_SIZE = 7

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
    10: (1,   3,  9),   11: (15,  3, 14),   12: (14,  6, 16),
}

CELL_W = EPD_WIDTH // COLS
CELL_H = (EPD_HEIGHT - 16) // ROWS
GRID_W = COLS * CELL_W
GRID_H = ROWS * CELL_H
MARGIN_X = (EPD_WIDTH - GRID_W) // 2
MARGIN_Y = (EPD_HEIGHT - GRID_H - 16) // 2
DOT_Y = MARGIN_Y + GRID_H + 8
DOT_R = 3
DOT_SPACING = 16


def _next_hour(h):
    return h % 12 + 1


def _add_word(active, word):
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
        h = _next_hour(h)
    nh = _next_hour(h)

    if m5 == 0:
        _add_word(active, HOURS_NOM[h])
    elif m5 == 5:
        _add_word(active, W_PYAT_M)
        _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 10:
        _add_word(active, W_DESYAT_M)
        _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 15:
        _add_word(active, W_CHETVERT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 20:
        _add_word(active, W_DVADTSAT)
        _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 25:
        _add_word(active, W_DVADTSAT)
        _add_word(active, W_PYAT_M)
        _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 30:
        _add_word(active, W_POLOVINA)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 35:
        _add_word(active, W_BEZ)
        _add_word(active, W_DVADTSATI)
        _add_word(active, W_PYATI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 40:
        _add_word(active, W_BEZ)
        _add_word(active, W_DVADTSATI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 45:
        _add_word(active, W_BEZ)
        _add_word(active, W_CHETVERTI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 50:
        _add_word(active, W_BEZ)
        _add_word(active, W_DESYATI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 55:
        _add_word(active, W_BEZ)
        _add_word(active, W_PYATI)
        _add_word(active, HOURS_NOM[nh])

    return active, plus_dots, minus_dots


def render(hour12, minute):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    active, plus_dots, minus_dots = active_positions(hour12, minute)

    img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    for row_idx, row_text in enumerate(GRID):
        for col_idx, char in enumerate(row_text):
            cx = MARGIN_X + col_idx * CELL_W
            cy = MARGIN_Y + row_idx * CELL_H

            bbox = font.getbbox(char)
            glyph_w = bbox[2] - bbox[0]
            glyph_h = bbox[3] - bbox[1]
            tx = cx + (CELL_W - glyph_w) // 2
            ty = cy + (CELL_H - glyph_h) // 2 - bbox[1]

            if (row_idx, col_idx) in active:
                draw.rectangle([cx, cy, cx + CELL_W - 1, cy + CELL_H - 1], fill=0)
                draw.text((tx, ty), char, font=font, fill=255)
            else:
                draw.text((tx, ty), char, font=font, fill=0)

    cx = EPD_WIDTH // 2
    gap = 5
    dot_positions = [
        cx - gap - DOT_SPACING - DOT_R,
        cx - gap - DOT_R,
        cx + gap + DOT_R,
        cx + gap + DOT_SPACING + DOT_R,
    ]
    for i, dx in enumerate(dot_positions):
        if i < 2:
            filled = (2 - i) <= minus_dots
        else:
            filled = (i - 1) <= plus_dots
        if filled:
            draw.ellipse([dx - DOT_R, DOT_Y - DOT_R, dx + DOT_R, DOT_Y + DOT_R], fill=0)
        else:
            draw.ellipse([dx - DOT_R, DOT_Y - DOT_R, dx + DOT_R, DOT_Y + DOT_R], outline=0)

    return img


if __name__ == "__main__":
    examples = [
        (12, 0), (1, 0), (7, 3), (5, 5), (3, 12),
        (7, 15), (8, 21), (5, 25), (11, 30),
        (6, 37), (2, 40), (9, 45), (4, 50), (10, 59),
    ]
    for h, m in examples:
        img = render(h, m)
        img.save(f"preview_ru_{h}_{m:02d}.png")

    img = render(7, 15)
    img.save("preview_ru.png")
    scaled = img.resize((EPD_WIDTH * 4, EPD_HEIGHT * 4), Image.NEAREST)
    scaled.save("preview_ru_4x.png")
    print(f"Saved preview_ru.png — 7:15 ЧЕТВЕРТЬ ВОСЬМОГО")
    print(f"Saved preview_ru_4x.png — 4x scaled")
