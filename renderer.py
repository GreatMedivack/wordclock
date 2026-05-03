import os
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 250
EPD_HEIGHT = 122

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "Silkscreen-Bold.ttf")
FONT_SIZE = 12

GRID = [
    "ONEXTWODTHREEIR",
    "FOURFIVESIXHATN",
    "SEVENREIGHTBULK",
    "NINETENVCELEVEN",
    "AMTWELVEXPMHOUR",
    "ZEROXONEDTWOBIA",
    "THREEGFOURFIVER",
    "ZEROXONETWOIAHD",
    "THREEFOURFIVESK",
    "SIXSEVENEIGHTLM",
    "NINEWORDCLOCKZX",
]

HOURS = {
    1:  (0, 0, 3),
    2:  (0, 4, 7),
    3:  (0, 8, 13),
    4:  (1, 0, 4),
    5:  (1, 4, 8),
    6:  (1, 8, 11),
    7:  (2, 0, 5),
    8:  (2, 6, 11),
    9:  (3, 0, 4),
    10: (3, 4, 7),
    11: (3, 9, 15),
    12: (4, 2, 8),
}

AMPM = {
    "AM": (4, 0, 2),
    "PM": (4, 9, 11),
}

TENS = {
    0: (5, 0, 4),
    1: (5, 5, 8),
    2: (5, 9, 12),
    3: (6, 0, 5),
    4: (6, 6, 10),
    5: (6, 10, 14),
}

ONES = {
    0: (7, 0, 4),
    1: (7, 5, 8),
    2: (7, 8, 11),
    3: (8, 0, 5),
    4: (8, 5, 9),
    5: (8, 9, 13),
    6: (9, 0, 3),
    7: (9, 3, 8),
    8: (9, 8, 13),
    9: (10, 0, 4),
}


def _active_positions(hour_12, tens_digit, ones_digit, ampm_str):
    active = set()
    for word_map, key in [
        (HOURS, hour_12),
        (TENS, tens_digit),
        (ONES, ones_digit),
        (AMPM, ampm_str),
    ]:
        row, col_start, col_end = word_map[key]
        for c in range(col_start, col_end):
            active.add((row, c))
    return active


def render(hour_12, tens_digit, ones_digit, ampm_str):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    cols = len(GRID[0])
    rows = len(GRID)

    cell_w = EPD_WIDTH // cols
    cell_h = EPD_HEIGHT // rows

    grid_w = cols * cell_w
    grid_h = rows * cell_h
    margin_x = (EPD_WIDTH - grid_w) // 2
    margin_y = (EPD_HEIGHT - grid_h) // 2

    img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    active = _active_positions(hour_12, tens_digit, ones_digit, ampm_str)

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
    img = render(3, 4, 7, "PM")
    img.save("preview.png")
    scaled = img.resize((EPD_WIDTH * 4, EPD_HEIGHT * 4), Image.NEAREST)
    scaled.save("preview_4x.png")
    print(f"Saved preview.png ({EPD_WIDTH}x{EPD_HEIGHT}) — showing 3:47 PM")
    print(f"Saved preview_4x.png ({EPD_WIDTH*4}x{EPD_HEIGHT*4}) — 4x scaled")
