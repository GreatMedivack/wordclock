#!/usr/bin/env python3
"""Russian word clock grid v2 — natural speech (QLOCKTWO-style).

Displays time as natural Russian expressions:
  ЧЕТВЕРТЬ ВОСЬМОГО    (7:15)
  БЕЗ ДЕСЯТИ ТРИ       (2:50)
  ПОЛОВИНА ДВЕНАДЦАТОГО (11:30)
  ДВАДЦАТЬ ПЯТЬ МИНУТ ШЕСТОГО (5:25)

Format (rounded to 5 min):
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

Grid: 16×16 = 256 LEDs
"""

COLS = 16
GRID = [
    "КГДВАДЦАТЬПЯТЬБЖ",  # 0:  ДВАДЦАТЬ ПЯТЬ
    "БВКДЕСЯТЬМИНУТГЖ",  # 1:  ДЕСЯТЬ МИНУТ
    "ЧЕТВЕРТЬПОЛОВИНА",  # 2:  ЧЕТВЕРТЬ ПОЛОВИНА
    "КГБЕЗПЯТИДЕСЯТИД",  # 3:  БЕЗ ПЯТИ ДЕСЯТИ
    "ДВАДЦАТИЧЕТВЕРТИ",  # 4:  ДВАДЦАТИ ЧЕТВЕРТИ
    "КПЕРВОГОВТОРОГОГ",  # 5:  ПЕРВОГО ВТОРОГО
    "ТРЕТЬЕГОДЕСЯТОГО",  # 6:  ТРЕТЬЕГО ДЕСЯТОГО
    "ЧЕТВЁРТОГОПЯТОГО",  # 7:  ЧЕТВЁРТОГО ПЯТОГО
    "ШЕСТОГОСЕДЬМОГОК",  # 8:  ШЕСТОГО СЕДЬМОГО
    "ВОСЬМОГОДЕВЯТОГО",  # 9:  ВОСЬМОГО ДЕВЯТОГО
    "КГОДИННАДЦАТОГОД",  # 10: ОДИННАДЦАТОГО
    "КГДВЕНАДЦАТОГОБД",  # 11: ДВЕНАДЦАТОГО
    "ЧАСДВАТРИЧЕТЫРЕК",  # 12: ЧАС ДВА ТРИ ЧЕТЫРЕ
    "ШЕСТЬСЕМЬВОСЕМЬК",  # 13: ШЕСТЬ СЕМЬ ВОСЕМЬ
    "ДЕВЯТЬДВЕНАДЦАТЬ",  # 14: ДЕВЯТЬ ДВЕНАДЦАТЬ
    "КГБОДИННАДЦАТЬДП",  # 15: ОДИННАДЦАТЬ
]
ROWS = len(GRID)

# ── Minute / modifier words ──
DVADTSAT  = (0, 2, 10)   # ДВАДЦАТЬ
PYAT      = (0, 10, 14)  # ПЯТЬ  (also nom. hour 5)
DESYAT    = (1, 3, 9)    # ДЕСЯТЬ (also nom. hour 10)
MINUT     = (1, 9, 14)   # МИНУТ
CHETVERT  = (2, 0, 8)    # ЧЕТВЕРТЬ
POLOVINA  = (2, 8, 16)   # ПОЛОВИНА
BEZ       = (3, 2, 5)    # БЕЗ
PYATI     = (3, 5, 9)    # ПЯТИ
DESYATI   = (3, 9, 15)   # ДЕСЯТИ
DVADTSATI = (4, 0, 8)    # ДВАДЦАТИ
CHETVERTI = (4, 8, 16)   # ЧЕТВЕРТИ

# ── Genitive hours (for "past": next hour after current) ──
HOURS_GEN = {
    1:  (5, 1, 8),    # ПЕРВОГО
    2:  (5, 8, 15),   # ВТОРОГО
    3:  (6, 0, 8),    # ТРЕТЬЕГО
    4:  (7, 0, 10),   # ЧЕТВЁРТОГО
    5:  (7, 10, 16),  # ПЯТОГО
    6:  (8, 0, 7),    # ШЕСТОГО
    7:  (8, 7, 15),   # СЕДЬМОГО
    8:  (9, 0, 8),    # ВОСЬМОГО
    9:  (9, 8, 16),   # ДЕВЯТОГО
    10: (6, 8, 16),   # ДЕСЯТОГО
    11: (10, 2, 15),  # ОДИННАДЦАТОГО
    12: (11, 2, 14),  # ДВЕНАДЦАТОГО
}

# ── Nominative hours (for "to" and :00) ──
#    ПЯТЬ and ДЕСЯТЬ are shared with minute words
HOURS_NOM = {
    1:  (12, 0, 3),   # ЧАС
    2:  (12, 3, 6),   # ДВА
    3:  (12, 6, 9),   # ТРИ
    4:  (12, 9, 15),  # ЧЕТЫРЕ
    5:  PYAT,          # ПЯТЬ (shared with row 0)
    6:  (13, 0, 5),   # ШЕСТЬ
    7:  (13, 5, 9),   # СЕМЬ
    8:  (13, 9, 15),  # ВОСЕМЬ
    9:  (14, 0, 6),   # ДЕВЯТЬ
    10: DESYAT,        # ДЕСЯТЬ (shared with row 1)
    11: (15, 3, 14),   # ОДИННАДЦАТЬ
    12: (14, 6, 16),  # ДВЕНАДЦАТЬ
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
        print(f"\n  ✓ Всё ОК. Сетка: {ROWS}×{COLS} = {ROWS * COLS} LED")
    return errors == 0


def next_hour(h):
    return h % 12 + 1


def time_words(hour12, minute):
    """Return (description, list of positions) for the given time rounded to 5 min."""
    minute = (minute // 5) * 5
    words = []
    parts = []

    if minute == 0:
        words.append(HOURS_NOM[hour12])
        parts.append(EXPECTED_NOM[hour12])
    elif minute <= 30:
        nh = next_hour(hour12)
        if minute == 5:
            words += [PYAT, MINUT]
            parts += ["ПЯТЬ", "МИНУТ"]
        elif minute == 10:
            words += [DESYAT, MINUT]
            parts += ["ДЕСЯТЬ", "МИНУТ"]
        elif minute == 15:
            words.append(CHETVERT)
            parts.append("ЧЕТВЕРТЬ")
        elif minute == 20:
            words += [DVADTSAT, MINUT]
            parts += ["ДВАДЦАТЬ", "МИНУТ"]
        elif minute == 25:
            words += [DVADTSAT, PYAT, MINUT]
            parts += ["ДВАДЦАТЬ", "ПЯТЬ", "МИНУТ"]
        elif minute == 30:
            words.append(POLOVINA)
            parts.append("ПОЛОВИНА")
        words.append(HOURS_GEN[nh])
        parts.append(EXPECTED_GEN[nh])
    else:
        nh = next_hour(hour12)
        words.append(BEZ)
        parts.append("БЕЗ")
        to_min = 60 - minute
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

    return " ".join(parts), words


def visualize(hour12, minute):
    minute_r = (minute // 5) * 5
    desc, positions = time_words(hour12, minute)

    active = set()
    for pos in positions:
        row, cs, ce = pos
        for c in range(cs, ce):
            active.add((row, c))

    print(f"\n  {hour12}:{minute_r:02d} → {desc}\n")
    for r, row_text in enumerate(GRID):
        line = "  "
        for c, ch in enumerate(row_text):
            if (r, c) in active:
                line += f"\033[97;42m {ch} \033[0m"
            else:
                line += f"\033[90m {ch} \033[0m"
        print(line)
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
        (5, 5),    # ПЯТЬ МИНУТ ШЕСТОГО
        (3, 10),   # ДЕСЯТЬ МИНУТ ЧЕТВЁРТОГО
        (7, 15),   # ЧЕТВЕРТЬ ВОСЬМОГО
        (8, 20),   # ДВАДЦАТЬ МИНУТ ДЕВЯТОГО
        (5, 25),   # ДВАДЦАТЬ ПЯТЬ МИНУТ ШЕСТОГО
        (11, 30),  # ПОЛОВИНА ДВЕНАДЦАТОГО
        (6, 35),   # БЕЗ ДВАДЦАТИ ПЯТИ СЕМЬ
        (2, 40),   # БЕЗ ДВАДЦАТИ ТРИ
        (9, 45),   # БЕЗ ЧЕТВЕРТИ ДЕСЯТЬ
        (4, 50),   # БЕЗ ДЕСЯТИ ПЯТЬ
        (10, 55),  # БЕЗ ПЯТИ ОДИННАДЦАТЬ
    ]
    for h, m in examples:
        visualize(h, m)
