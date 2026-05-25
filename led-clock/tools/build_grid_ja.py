#!/usr/bin/env python3
"""Build and validate Japanese word clock grid (8×10 kanji matrix).

Displays time as: 午後 五時 四七分 (5:47 PM)
Components: 午前/午後 + hour(1-12) + 時 + tens(0-5) + ones(0-9) + 分
Decorative: 時計 (tokei = clock)
"""

COLS = 10
GRID = [
    "午前花午後雲時計夢光",  # 0: 午前 午後 時計
    "一雪二風三山四森五泉",  # 1: Hours 1-5
    "六波七虹八鳥九竹時霧",  # 2: Hours 6-9, 時
    "十露十一霜十二月雪空",  # 3: Hours 10,11,12
    "〇火一水二木三金四土",  # 4: Tens 0-4
    "五雨〇石一霧二夢三露",  # 5: Tens 5, Ones 0-3
    "四竹五花六雪七音八鳥",  # 6: Ones 4-8
    "九海川山森泉波虹風分",  # 7: Ones 9, 分
]
ROWS = len(GRID)

AMPM = {
    "AM": (0, 0, 2),   # 午前
    "PM": (0, 3, 5),   # 午後
}

HOURS = {
    1:  (1, 0, 1),     # 一
    2:  (1, 2, 3),     # 二
    3:  (1, 4, 5),     # 三
    4:  (1, 6, 7),     # 四
    5:  (1, 8, 9),     # 五
    6:  (2, 0, 1),     # 六
    7:  (2, 2, 3),     # 七
    8:  (2, 4, 5),     # 八
    9:  (2, 6, 7),     # 九
    10: (3, 0, 1),     # 十
    11: (3, 2, 4),     # 十一
    12: (3, 5, 7),     # 十二
}

HOUR_SUFFIX = (2, 8, 9)   # 時

TENS = {
    0: (4, 0, 1),     # 〇
    1: (4, 2, 3),     # 一
    2: (4, 4, 5),     # 二
    3: (4, 6, 7),     # 三
    4: (4, 8, 9),     # 四
    5: (5, 0, 1),     # 五
}

ONES = {
    0: (5, 2, 3),     # 〇
    1: (5, 4, 5),     # 一
    2: (5, 6, 7),     # 二
    3: (5, 8, 9),     # 三
    4: (6, 0, 1),     # 四
    5: (6, 2, 3),     # 五
    6: (6, 4, 5),     # 六
    7: (6, 6, 7),     # 七
    8: (6, 8, 9),     # 八
    9: (7, 0, 1),     # 九
}

MINUTE_SUFFIX = (7, 9, 10)  # 分

DECOR = (0, 6, 8)          # 時計

EXPECTED = {
    "AMPM": {"AM": "午前", "PM": "午後"},
    "HOURS": {
        1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
        6: "六", 7: "七", 8: "八", 9: "九", 10: "十",
        11: "十一", 12: "十二",
    },
    "TENS": {0: "〇", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五"},
    "ONES": {
        0: "〇", 1: "一", 2: "二", 3: "三", 4: "四",
        5: "五", 6: "六", 7: "七", 8: "八", 9: "九",
    },
}


def verify():
    errors = 0
    for i, row in enumerate(GRID):
        n = len(row)
        if n != COLS:
            print(f"  ERROR: row {i} has {n} chars, expected {COLS}: \"{row}\"")
            errors += 1

    for name, mapping in [("AMPM", AMPM), ("HOURS", HOURS), ("TENS", TENS), ("ONES", ONES)]:
        for key, (row, cs, ce) in mapping.items():
            word = GRID[row][cs:ce]
            expected = EXPECTED[name][key]
            ok = "✓" if word == expected else f"✗ expected \"{expected}\""
            print(f"  {name}[{key!r:>4}] = row {row} [{cs}:{ce}] → \"{word}\" {ok}")
            if word != expected:
                errors += 1

    for label, (row, cs, ce) in [("時", HOUR_SUFFIX), ("分", MINUTE_SUFFIX), ("時計", DECOR)]:
        word = GRID[row][cs:ce]
        ok = "✓" if word == label else f"✗ expected \"{label}\""
        print(f"  FIXED[{label!r:>4}] = row {row} [{cs}:{ce}] → \"{word}\" {ok}")
        if word != label:
            errors += 1

    if errors:
        print(f"\n  {errors} ERRORS!")
    else:
        print(f"\n  All OK. Grid: {ROWS}×{COLS} = {ROWS * COLS} LEDs")
    return errors == 0


if __name__ == "__main__":
    verify()
