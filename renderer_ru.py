import os
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 250
EPD_HEIGHT = 122

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "LiberationMono-Bold.ttf")
FONT_SIZE = 6

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


def _next_hour(h):
    return h % 12 + 1


def _add_word(active, word):
    r, cs, ce = word
    for c in range(cs, ce):
        active.add((r, c))


def _active_positions(hour12, minute):
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
        _add_word(active, W_PYAT_M); _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 10:
        _add_word(active, W_DESYAT_M); _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 15:
        _add_word(active, W_CHETVERT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 20:
        _add_word(active, W_DVADTSAT); _add_word(active, W_MINUT)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 25:
        _add_word(active, W_DVADTSAT); _add_word(active, W_PYAT_M)
        _add_word(active, W_MINUT); _add_word(active, HOURS_GEN[nh])
    elif m5 == 30:
        _add_word(active, W_POLOVINA)
        _add_word(active, HOURS_GEN[nh])
    elif m5 == 35:
        _add_word(active, W_BEZ); _add_word(active, W_DVADTSATI)
        _add_word(active, W_PYATI); _add_word(active, HOURS_NOM[nh])
    elif m5 == 40:
        _add_word(active, W_BEZ); _add_word(active, W_DVADTSATI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 45:
        _add_word(active, W_BEZ); _add_word(active, W_CHETVERTI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 50:
        _add_word(active, W_BEZ); _add_word(active, W_DESYATI)
        _add_word(active, HOURS_NOM[nh])
    elif m5 == 55:
        _add_word(active, W_BEZ); _add_word(active, W_PYATI)
        _add_word(active, HOURS_NOM[nh])

    return active, plus_dots, minus_dots


def render(hour12, minute):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    cell_w = EPD_WIDTH // COLS
    cell_h = (EPD_HEIGHT - 10) // ROWS
    grid_w = COLS * cell_w
    grid_h = ROWS * cell_h
    margin_x = (EPD_WIDTH - grid_w) // 2
    margin_y = (EPD_HEIGHT - 10 - grid_h) // 2

    img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    active, plus_dots, minus_dots = _active_positions(hour12, minute)

    for row_idx, row_text in enumerate(GRID):
        for col_idx, char in enumerate(row_text):
            cx = margin_x + col_idx * cell_w
            cy = margin_y + row_idx * cell_h

            bbox = font.getbbox(char)
            glyph_w = bbox[2] - bbox[0]
            glyph_h = bbox[3] - bbox[1]
            tx = cx + (cell_w - glyph_w) // 2
            ty = cy + (cell_h - glyph_h) // 2 - bbox[1]

            if (row_idx, col_idx) in active:
                draw.rectangle([cx, cy, cx + cell_w - 1, cy + cell_h - 1], fill=0)
                draw.text((tx, ty), char, font=font, fill=255)
            else:
                draw.text((tx, ty), char, font=font, fill=0)

    dot_y = margin_y + grid_h + 5
    dot_r = 2
    center_x = EPD_WIDTH // 2
    gap = 8
    pair_sp = 5
    dot_xs = [
        center_x - gap - pair_sp,
        center_x - gap,
        center_x + gap,
        center_x + gap + pair_sp,
    ]
    for i, dx in enumerate(dot_xs):
        if i < 2:
            filled = (2 - i) <= minus_dots
        else:
            filled = (i - 1) <= plus_dots
        if filled:
            draw.ellipse([dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r], fill=0)
        else:
            draw.ellipse([dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r], outline=0)

    return img


if __name__ == "__main__":
    examples = [
        (12, 0), (1, 0), (7, 2), (5, 5), (7, 15),
        (5, 25), (11, 30), (6, 38), (9, 45), (4, 50), (12, 58),
    ]
    for h, m in examples:
        img = render(h, m)
        img.save(f"preview_ru_{h}_{m:02d}.png")

    img = render(5, 47)
    img.save("preview_ru.png")
    scaled = img.resize((EPD_WIDTH * 4, EPD_HEIGHT * 4), Image.NEAREST)
    scaled.save("preview_ru_4x.png")
    print(f"Saved: preview_ru.png (5:47)")
