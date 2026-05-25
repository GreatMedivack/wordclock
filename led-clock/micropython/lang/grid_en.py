"""English word clock grid — 11×15 (original)."""

COLS = 15
ROWS = 11
LANG = "en"

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
    1:  (0, 0, 3),   2:  (0, 4, 7),   3:  (0, 8, 13),
    4:  (1, 0, 4),   5:  (1, 4, 8),   6:  (1, 8, 11),
    7:  (2, 0, 5),   8:  (2, 6, 11),  9:  (3, 0, 4),
    10: (3, 4, 7),   11: (3, 9, 15),  12: (4, 2, 8),
}

AMPM = {"AM": (4, 0, 2), "PM": (4, 9, 11)}

TENS = {
    0: (5, 0, 4),  1: (5, 5, 8),   2: (5, 9, 12),
    3: (6, 0, 5),  4: (6, 6, 10),  5: (6, 10, 14),
}

ONES = {
    0: (7, 0, 4),  1: (7, 5, 8),   2: (7, 8, 11),
    3: (8, 0, 5),  4: (8, 5, 9),   5: (8, 9, 13),
    6: (9, 0, 3),  7: (9, 3, 8),   8: (9, 8, 13),
    9: (10, 0, 4),
}

FIXED = []
