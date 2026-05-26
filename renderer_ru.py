import os
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 250
EPD_HEIGHT = 122

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "LiberationMono-Bold.ttf")
FONT_SIZE = 8

GRID = [
    "ОДИНЖДВАЮТРИБШП",
    "ЧЕТЫРЕЛПЯТЬГУКМ",
    "ШЕСТЬЖСЕМЬГДЦУХ",
    "ВОСЕМЬХДЕВЯТЬЙШ",
    "ДЕСЯТЬЛКМБЦУЖФХ",
    "ОДИННАДЦАТЬГУКМ",
    "ДВЕНАДЦАТЬДНЖНЧ",
    "НОЛЬЖОДИНРДВАБЧ",
    "ТРИГЧЕТЫРЕКПЯТЬ",
    "НОЛЬЮОДИНМДВАВУ",
    "ТРИЗЧЕТЫРЕХПЯТЬ",
    "ШЕСТЬСЕМЬВОСЕМЬ",
    "ДЕВЯТЬЧАСЫЖКЛМН",
]

COLS = 15
ROWS = 13

HOURS = {
    1:  (0, 0, 4),   2:  (0, 5, 8),   3:  (0, 9, 12),
    4:  (1, 0, 6),   5:  (1, 7, 11),  6:  (2, 0, 5),
    7:  (2, 6, 10),  8:  (3, 0, 6),   9:  (3, 7, 13),
    10: (4, 0, 6),   11: (5, 0, 11),  12: (6, 0, 10),
}

AMPM = {"AM": (6, 10, 12), "PM": (6, 13, 15)}

TENS = {
    0: (7, 0, 4),   1: (7, 5, 9),   2: (7, 10, 13),
    3: (8, 0, 3),   4: (8, 4, 10),  5: (8, 11, 15),
}

ONES = {
    0: (9, 0, 4),   1: (9, 5, 9),   2: (9, 10, 13),
    3: (10, 0, 3),  4: (10, 4, 10), 5: (10, 11, 15),
    6: (11, 0, 5),  7: (11, 5, 9),  8: (11, 9, 15),
    9: (12, 0, 6),
}


def _active_positions(hour12, tens_digit, ones_digit, ampm_str):
    active = set()
    for word_map, key in [
        (HOURS, hour12),
        (AMPM, ampm_str),
        (TENS, tens_digit),
        (ONES, ones_digit),
    ]:
        row, col_start, col_end = word_map[key]
        for c in range(col_start, col_end):
            active.add((row, c))
    return active


def render(hour12, tens_digit, ones_digit, ampm_str):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    cell_w = EPD_WIDTH // COLS
    cell_h = EPD_HEIGHT // ROWS
    grid_w = COLS * cell_w
    grid_h = ROWS * cell_h
    margin_x = (EPD_WIDTH - grid_w) // 2
    margin_y = (EPD_HEIGHT - grid_h) // 2

    img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    active = _active_positions(hour12, tens_digit, ones_digit, ampm_str)

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

    return img


if __name__ == "__main__":
    EXPECTED = {
        "HOURS": {
            1: "ОДИН", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ",
            6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ", 10: "ДЕСЯТЬ",
            11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
        },
        "AMPM": {"AM": "ДН", "PM": "НЧ"},
        "TENS": {0: "НОЛЬ", 1: "ОДИН", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ"},
        "ONES": {
            0: "НОЛЬ", 1: "ОДИН", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ",
            6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ",
        },
    }

    errors = 0
    for i, row in enumerate(GRID):
        if len(row) != COLS:
            print(f"ERROR: row {i} has {len(row)} chars, expected {COLS}")
            errors += 1

    for name, mapping in [("HOURS", HOURS), ("AMPM", AMPM), ("TENS", TENS), ("ONES", ONES)]:
        print(f"── {name} ──")
        for key, (row, cs, ce) in mapping.items():
            word = GRID[row][cs:ce]
            exp = EXPECTED[name][key]
            ok = "✓" if word == exp else f"✗ got '{word}'"
            print(f"  {str(key):>4} → {exp:>12} = row {row:>2} [{cs:>2}:{ce:>2}] → '{word}' {ok}")
            if word != exp:
                errors += 1

    if errors:
        print(f"\n{errors} ОШИБОК!")
        exit(1)

    print(f"\n✓ Сетка ОК: {ROWS}×{COLS} = {ROWS * COLS} ячеек\n")

    examples = [
        (12, 0, 0, "AM"), (1, 0, 7, "AM"), (5, 4, 7, "PM"),
        (3, 1, 0, "PM"), (11, 2, 3, "PM"), (7, 1, 5, "AM"),
    ]
    for h, t, o, ap in examples:
        print(f"  {h}:{t}{o} {ap} → {EXPECTED['HOURS'][h]} {EXPECTED['AMPM'][ap]} {EXPECTED['TENS'][t]} {EXPECTED['ONES'][o]}")

    img = render(5, 4, 7, "PM")
    img.save("preview_ru.png")
    scaled = img.resize((EPD_WIDTH * 4, EPD_HEIGHT * 4), Image.NEAREST)
    scaled.save("preview_ru_4x.png")
    print(f"\nСохранено: preview_ru.png — 5:47 PM → ПЯТЬ НЧ ЧЕТЫРЕ СЕМЬ")
