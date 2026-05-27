#!/usr/bin/env python3
"""Russian word clock grid v2 — natural speech (QLOCKTWO-style).

Displays time as natural Russian expressions:
  ЧЕТВЕРТЬ ВОСЬМОГО    (7:15)
  БЕЗ ДЕСЯТИ ТРИ       (2:50)
  ПОЛОВИНА ДВЕНАДЦАТОГО (11:30)
  ДВАДЦАТЬ ПЯТЬ МИНУТ ШЕСТОГО (5:25)

Format (5-min words + dot indicators for exact minutes):
  :00  [HOUR nom]
  :05  ПЯТЬ МИНУТ [HOUR+1 gen]
  :10  ДЕСЯТЬ МИНУТ [HOUR+1 gen]
  :15  ЧЕТВЕРТЬ [HOUR+1 gen]
  :20  ДВАДЦАТЬ МИНУТ [HOUR+1 gen]
  :25  ДВАДЦАТЬ ПЯТЬ МИНУТ [HOUR+1 gen]
  :30  ПОЛОВИНА [HOUR+1 gen]
  :35  БЕЗ ДВАДЦАТИ ПЯТИ [HOUR+1 nom]
  :40  БЕЗ ДВАДЦАТИ [HOUR+1 nom]
  :45  БЕЗ ЧЕТВЕРТИ [HOUR+1 nom]
  :50  БЕЗ ДЕСЯТИ [HOUR+1 nom]
  :55  БЕЗ ПЯТИ [HOUR+1 nom]

  + 4 dot LEDs (256-259): left pair = minus, right pair = plus (±2 minutes)

Grid: 16×16 = 256 LEDs + 4 dots = 260 LEDs total
"""

COLS = 16
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
ROWS = len(GRID)

# ── Minute / modifier words ──
DVADTSAT  = (0,  1,  9)  # ДВАДЦАТЬ
PYAT      = (0, 10, 14)  # ПЯТЬ (minute)
DESYAT    = (1,  2,  8)  # ДЕСЯТЬ (minute)
MINUT     = (1,  9, 14)  # МИНУТ
CHETVERT  = (2,  0,  8)  # ЧЕТВЕРТЬ
POLOVINA  = (2,  8, 16)  # ПОЛОВИНА
BEZ       = (3,  1,  4)  # БЕЗ
DVADTSATI = (3,  5, 13)  # ДВАДЦАТИ
PYATI     = (4,  0,  4)  # ПЯТИ
DESYATI   = (5,  0,  6)  # ДЕСЯТИ
CHETVERTI = (4,  5, 13)  # ЧЕТВЕРТИ

# ── Genitive hours (for "past": next hour after current) ──
HOURS_GEN = {
    1:  (5,  6, 13),  # ПЕРВОГО
    2:  (6,  0,  7),  # ВТОРОГО
    3:  (7,  0,  8),  # ТРЕТЬЕГО
    4:  (8,  0, 10),  # ЧЕТВЁРТОГО
    5:  (6,  7, 13),  # ПЯТОГО
    6:  (7,  8, 15),  # ШЕСТОГО
    7:  (9,  0,  8),  # СЕДЬМОГО
    8:  (9,  8, 16),  # ВОСЬМОГО
    9:  (10, 0,  8),  # ДЕВЯТОГО
    10: (10, 8, 16),  # ДЕСЯТОГО
    11: (11, 0, 13),  # ОДИННАДЦАТОГО
    12: (12, 0, 12),  # ДВЕНАДЦАТОГО
}

# ── Nominative hours (for "to" and :00) ──
HOURS_NOM = {
    1:  (6,  13, 16),  # ЧАС
    2:  (11, 13, 16),  # ДВА
    3:  (5,  13, 16),  # ТРИ
    4:  (8,  10, 16),  # ЧЕТЫРЕ
    5:  (12, 12, 16),  # ПЯТЬ
    6:  (14, 11, 16),  # ШЕСТЬ
    7:  (15,  0,  4),  # СЕМЬ
    8:  (15,  4, 10),  # ВОСЕМЬ
    9:  (15, 10, 16),  # ДЕВЯТЬ
    10: (13, 10, 16),  # ДЕСЯТЬ
    11: (14,  0, 11),  # ОДИННАДЦАТЬ
    12: (13,  0, 10),  # ДВЕНАДЦАТЬ
}

# ── Expected strings for validation ──
EXPECTED_GEN = {
    1: "ПЕРВОГО", 2: "ВТОРОГО", 3: "ТРЕТЬЕГО", 4: "ЧЕТВЁРТОГО",
    5: "ПЯТОГО", 6: "ШЕСТОГО", 7: "СЕДЬМОГО", 8: "ВОСЬМОГО",
    9: "ДЕВЯТОГО", 10: "ДЕСЯТОГО", 11: "ОДИННАДЦАТОГО", 12: "ДВЕНАДЦАТОГО",
}
EXPECTED_NOM = {
    1: "ЧАС", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ",
    5: "ПЯТЬ", 6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ",
    9: "ДЕВЯТЬ", 10: "ДЕСЯТЬ", 11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
}
EXPECTED_MISC = {
    "ДВАДЦАТЬ": DVADTSAT, "ПЯТЬ": PYAT,
    "ДЕСЯТЬ": DESYAT, "МИНУТ": MINUT, "ЧЕТВЕРТЬ": CHETVERT,
    "ПОЛОВИНА": POLOVINA, "БЕЗ": BEZ, "ПЯТИ": PYATI,
    "ДЕСЯТИ": DESYATI, "ДВАДЦАТИ": DVADTSATI, "ЧЕТВЕРТИ": CHETVERTI,
}


def get_word(pos):
    row, cs, ce = pos
    return GRID[row][cs:ce]


def verify():
    errors = 0
    for i, row in enumerate(GRID):
        if len(row) != COLS:
            print(f"  ERROR: row {i} has {len(row)} chars, expected {COLS}: \"{row}\"")
            errors += 1

    print("  ── Слова минут и модификаторы ──")
    for name, pos in EXPECTED_MISC.items():
        word = get_word(pos)
        ok = "✓" if word == name else f"✗ got \"{word}\""
        print(f"    {name:>12} = row {pos[0]:>2} [{pos[1]:>2}:{pos[2]:>2}] → \"{word}\" {ok}")
        if word != name:
            errors += 1

    print("\n  ── Часы — родительный падеж (для «минут ... -ого») ──")
    for h in range(1, 13):
        pos = HOURS_GEN[h]
        word = get_word(pos)
        exp = EXPECTED_GEN[h]
        ok = "✓" if word == exp else f"✗ got \"{word}\""
        print(f"    {h:>2} → {exp:>15} = row {pos[0]:>2} [{pos[1]:>2}:{pos[2]:>2}] → \"{word}\" {ok}")
        if word != exp:
            errors += 1

    print("\n  ── Часы — именительный падеж (для «без ... » и :00) ──")
    for h in range(1, 13):
        pos = HOURS_NOM[h]
        word = get_word(pos)
        exp = EXPECTED_NOM[h]
        ok = "✓" if word == exp else f"✗ got \"{word}\""
        print(f"    {h:>2} → {exp:>12} = row {pos[0]:>2} [{pos[1]:>2}:{pos[2]:>2}] → \"{word}\" {ok}")
        if word != exp:
            errors += 1

    if errors:
        print(f"\n  {errors} ОШИБОК!")
    else:
        print(f"\n  ✓ Всё ОК. Сетка: {ROWS}×{COLS} = {ROWS * COLS} LED + 4 dots = {ROWS * COLS + 4} LED")
    return errors == 0


def next_hour(h):
    return h % 12 + 1


def time_words(hour12, minute):
    """Return (description, list of positions, plus_dots, minus_dots) for the given time."""
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

    words = []
    parts = []

    if m5 == 0:
        words.append(HOURS_NOM[h])
        parts.append(EXPECTED_NOM[h])
    elif m5 <= 30:
        nh = next_hour(h)
        if m5 == 5:
            words += [PYAT, MINUT]
            parts += ["ПЯТЬ", "МИНУТ"]
        elif m5 == 10:
            words += [DESYAT, MINUT]
            parts += ["ДЕСЯТЬ", "МИНУТ"]
        elif m5 == 15:
            words.append(CHETVERT)
            parts.append("ЧЕТВЕРТЬ")
        elif m5 == 20:
            words += [DVADTSAT, MINUT]
            parts += ["ДВАДЦАТЬ", "МИНУТ"]
        elif m5 == 25:
            words += [DVADTSAT, PYAT, MINUT]
            parts += ["ДВАДЦАТЬ", "ПЯТЬ", "МИНУТ"]
        elif m5 == 30:
            words.append(POLOVINA)
            parts.append("ПОЛОВИНА")
        words.append(HOURS_GEN[nh])
        parts.append(EXPECTED_GEN[nh])
    else:
        nh = next_hour(h)
        words.append(BEZ)
        parts.append("БЕЗ")
        to_min = 60 - m5
        if to_min == 25:
            words += [DVADTSATI, PYATI]
            parts += ["ДВАДЦАТИ", "ПЯТИ"]
        elif to_min == 20:
            words.append(DVADTSATI)
            parts.append("ДВАДЦАТИ")
        elif to_min == 15:
            words.append(CHETVERTI)
            parts.append("ЧЕТВЕРТИ")
        elif to_min == 10:
            words.append(DESYATI)
            parts.append("ДЕСЯТИ")
        elif to_min == 5:
            words.append(PYATI)
            parts.append("ПЯТИ")
        words.append(HOURS_NOM[nh])
        parts.append(EXPECTED_NOM[nh])

    desc = " ".join(parts)
    if minus_dots:
        desc += f" −{'●' * minus_dots}"
    if plus_dots:
        desc += f" +{'●' * plus_dots}"
    return desc, words, plus_dots, minus_dots


def visualize(hour12, minute):
    desc, positions, plus_dots, minus_dots = time_words(hour12, minute)

    active = set()
    for pos in positions:
        row, cs, ce = pos
        for c in range(cs, ce):
            active.add((row, c))

    print(f"\n  {hour12}:{minute:02d} → {desc}\n")
    for r, row_text in enumerate(GRID):
        line = "  "
        for c, ch in enumerate(row_text):
            if (r, c) in active:
                line += f"\033[97;42m {ch} \033[0m"
            else:
                line += f"\033[90m {ch} \033[0m"
        print(line)
    if minus_dots or plus_dots:
        dot_line = "  " + " " * 16
        # Left pair (minus, from center outward)
        for i in range(2):
            if (2 - i) <= minus_dots:
                dot_line += f"\033[97;41m ● \033[0m "
            else:
                dot_line += f"\033[90m ○ \033[0m "
        dot_line += "  "
        # Right pair (plus, from center outward)
        for i in range(2):
            if (i + 1) <= plus_dots:
                dot_line += f"\033[97;42m ● \033[0m "
            else:
                dot_line += f"\033[90m ○ \033[0m "
        print(dot_line)
    print()


if __name__ == "__main__":
    print("\n  ═══ Русские буквенные часы v2 — разговорный формат ═══")
    print(f"  ═══ Сетка {ROWS}×{COLS} = {ROWS * COLS} LED ═══\n")

    ok = verify()
    if not ok:
        exit(1)

    examples = [
        (12, 0),   # ДВЕНАДЦАТЬ
        (1, 0),    # ЧАС
        (7, 2),    # СЕМЬ +●●
        (5, 5),    # ПЯТЬ МИНУТ ШЕСТОГО
        (3, 13),   # ЧЕТВЕРТЬ ЧЕТВЁРТОГО −●●
        (7, 15),   # ЧЕТВЕРТЬ ВОСЬМОГО
        (8, 22),   # ДВАДЦАТЬ МИНУТ ДЕВЯТОГО +●●
        (5, 25),   # ДВАДЦАТЬ ПЯТЬ МИНУТ ШЕСТОГО
        (11, 29),  # ПОЛОВИНА ДВЕНАДЦАТОГО −●
        (11, 30),  # ПОЛОВИНА ДВЕНАДЦАТОГО
        (6, 38),   # БЕЗ ДВАДЦАТИ СЕМЬ −●●
        (2, 40),   # БЕЗ ДВАДЦАТИ ТРИ
        (9, 44),   # БЕЗ ЧЕТВЕРТИ ДЕСЯТЬ −●
        (4, 50),   # БЕЗ ДЕСЯТИ ПЯТЬ
        (12, 58),  # ЧАС −●●
    ]
    for h, m in examples:
        visualize(h, m)
