#!/usr/bin/env python3
"""Exhaustive grid v4 correctness tests.

Checks every possible time (12h × 60min = 720 variants):
  1. All word positions resolve to correct Russian text in the grid
  2. No two co-active words touch or overlap on the same row
  3. Visual reading order (top→bottom, left→right) matches logical phrase order
"""

import sys

GRID = [
    "ГДВАДЦАТЬГПЯТЬГЖ",  #  0
    "ЖГДЕСЯТЬГМИНУТГЖ",  #  1
    "ЧЕТВЕРТЬПОЛОВИНА",  #  2
    "ГБЕЗГДВАДЦАТИГЖГ",  #  3
    "ПЯТИГЧЕТВЕРТИГГГ",  #  4
    "ДЕСЯТИПЕРВОГОТРИ",  #  5
    "ВТОРОГОПЯТОГОЧАС",  #  6
    "ТРЕТЬЕГОШЕСТОГОГ",  #  7
    "ЧЕТВЁРТОГОЧЕТЫРЕ",  #  8
    "СЕДЬМОГОВОСЬМОГО",  #  9
    "ДЕВЯТОГОДЕСЯТОГО",  # 10
    "ОДИННАДЦАТОГОДВА",  # 11
    "ДВЕНАДЦАТОГОПЯТЬ",  # 12
    "ДВЕНАДЦАТЬДЕСЯТЬ",  # 13
    "ОДИННАДЦАТЬШЕСТЬ",  # 14
    "СЕМЬВОСЕМЬДЕВЯТЬ",  # 15
]

COLS = 16

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

EXPECTED_GEN = {
    1: "ПЕРВОГО", 2: "ВТОРОГО", 3: "ТРЕТЬЕГО", 4: "ЧЕТВЁРТОГО",
    5: "ПЯТОГО", 6: "ШЕСТОГО", 7: "СЕДЬМОГО", 8: "ВОСЬМОГО",
    9: "ДЕВЯТОГО", 10: "ДЕСЯТОГО", 11: "ОДИННАДЦАТОГО", 12: "ДВЕНАДЦАТОГО",
}
EXPECTED_NOM = {
    1: "ЧАС", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ",
    6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ", 10: "ДЕСЯТЬ",
    11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
}
EXPECTED_MOD = {
    "ДВАДЦАТЬ": W_DVADTSAT, "ПЯТЬ": W_PYAT_M,
    "ДЕСЯТЬ": W_DESYAT_M, "МИНУТ": W_MINUT,
    "ЧЕТВЕРТЬ": W_CHETVERT, "ПОЛОВИНА": W_POLOVINA,
    "БЕЗ": W_BEZ, "ДВАДЦАТИ": W_DVADTSATI,
    "ПЯТИ": W_PYATI, "ДЕСЯТИ": W_DESYATI,
    "ЧЕТВЕРТИ": W_CHETVERTI,
}


def grid_word(pos):
    row, cs, ce = pos
    return GRID[row][cs:ce]


def next_hour(h):
    return h % 12 + 1


def get_words(hour12, minute):
    """Return list of (word_position, label) tuples in logical phrase order."""
    remainder = minute % 5
    if remainder <= 2:
        m5 = (minute // 5) * 5
    else:
        m5 = (minute // 5) * 5 + 5

    h = hour12
    if m5 == 60:
        m5 = 0
        h = next_hour(h)
    nh = next_hour(h)

    words = []
    if m5 == 0:
        words.append((HOURS_NOM[h], EXPECTED_NOM[h]))
    elif m5 == 5:
        words += [(W_PYAT_M, "ПЯТЬ"), (W_MINUT, "МИНУТ"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 10:
        words += [(W_DESYAT_M, "ДЕСЯТЬ"), (W_MINUT, "МИНУТ"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 15:
        words += [(W_CHETVERT, "ЧЕТВЕРТЬ"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 20:
        words += [(W_DVADTSAT, "ДВАДЦАТЬ"), (W_MINUT, "МИНУТ"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 25:
        words += [(W_DVADTSAT, "ДВАДЦАТЬ"), (W_PYAT_M, "ПЯТЬ"), (W_MINUT, "МИНУТ"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 30:
        words += [(W_POLOVINA, "ПОЛОВИНА"), (HOURS_GEN[nh], EXPECTED_GEN[nh])]
    elif m5 == 35:
        words += [(W_BEZ, "БЕЗ"), (W_DVADTSATI, "ДВАДЦАТИ"), (W_PYATI, "ПЯТИ"), (HOURS_NOM[nh], EXPECTED_NOM[nh])]
    elif m5 == 40:
        words += [(W_BEZ, "БЕЗ"), (W_DVADTSATI, "ДВАДЦАТИ"), (HOURS_NOM[nh], EXPECTED_NOM[nh])]
    elif m5 == 45:
        words += [(W_BEZ, "БЕЗ"), (W_CHETVERTI, "ЧЕТВЕРТИ"), (HOURS_NOM[nh], EXPECTED_NOM[nh])]
    elif m5 == 50:
        words += [(W_BEZ, "БЕЗ"), (W_DESYATI, "ДЕСЯТИ"), (HOURS_NOM[nh], EXPECTED_NOM[nh])]
    elif m5 == 55:
        words += [(W_BEZ, "БЕЗ"), (W_PYATI, "ПЯТИ"), (HOURS_NOM[nh], EXPECTED_NOM[nh])]
    return words


def fmt_time(h, m):
    return f"{h}:{m:02d}"


# ═══════════════════════════════════════════════════════════════════
#  Test 1: Grid geometry — every row is 16 chars
# ═══════════════════════════════════════════════════════════════════
def test_grid_dimensions():
    errors = []
    if len(GRID) != 16:
        errors.append(f"Grid has {len(GRID)} rows, expected 16")
    for i, row in enumerate(GRID):
        if len(row) != COLS:
            errors.append(f"Row {i}: {len(row)} chars, expected {COLS}")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Test 2: Every word position resolves to correct text
# ═══════════════════════════════════════════════════════════════════
def test_word_positions():
    errors = []
    for label, pos in EXPECTED_MOD.items():
        actual = grid_word(pos)
        if actual != label:
            errors.append(f"Modifier {label}: expected '{label}', got '{actual}' at {pos}")
    for h in range(1, 13):
        actual = grid_word(HOURS_GEN[h])
        exp = EXPECTED_GEN[h]
        if actual != exp:
            errors.append(f"GEN_{h}: expected '{exp}', got '{actual}' at {HOURS_GEN[h]}")
    for h in range(1, 13):
        actual = grid_word(HOURS_NOM[h])
        exp = EXPECTED_NOM[h]
        if actual != exp:
            errors.append(f"NOM_{h}: expected '{exp}', got '{actual}' at {HOURS_NOM[h]}")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Test 3: No co-active words touch or overlap on the same row
# ═══════════════════════════════════════════════════════════════════
def test_no_collisions():
    errors = []
    seen = set()
    for h in range(1, 13):
        for m in range(60):
            words = get_words(h, m)
            by_row = {}
            for pos, label in words:
                row, cs, ce = pos
                by_row.setdefault(row, []).append((cs, ce, label))
            for row, items in by_row.items():
                if len(items) < 2:
                    continue
                items.sort()
                for i in range(len(items) - 1):
                    cs1, ce1, l1 = items[i]
                    cs2, ce2, l2 = items[i + 1]
                    if ce1 > cs2:
                        key = (l1, l2)
                        if key not in seen:
                            seen.add(key)
                            errors.append(
                                f"{fmt_time(h,m)}: '{l1}'[:{ce1}] overlaps '{l2}'[{cs2}:] on row {row}")
                    elif ce1 == cs2:
                        key = (l1, l2)
                        if key not in seen:
                            seen.add(key)
                            errors.append(
                                f"{fmt_time(h,m)}: '{l1}'[:{ce1}] touches '{l2}'[{cs2}:] on row {row}")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Test 4: Reading order — visual (top→bottom, left→right) matches
#          logical Russian phrase order for all 720 time variants
# ═══════════════════════════════════════════════════════════════════
def test_reading_order():
    errors = []
    seen_phrases = set()
    for h in range(1, 13):
        for m in range(60):
            words = get_words(h, m)
            if len(words) < 2:
                continue
            logical = [label for _, label in words]
            visual = sorted(words, key=lambda w: (w[0][0], w[0][1]))
            visual_labels = [label for _, label in visual]
            if visual_labels != logical:
                phrase = " ".join(logical)
                if phrase not in seen_phrases:
                    seen_phrases.add(phrase)
                    errors.append(
                        f"{fmt_time(h,m)}: should read «{phrase}» "
                        f"but grid reads «{' '.join(visual_labels)}»")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Test 5: Every 5-min slot (144 total) produces at least one word
# ═══════════════════════════════════════════════════════════════════
def test_all_slots_covered():
    errors = []
    for h in range(1, 13):
        for m5 in range(0, 60, 5):
            words = get_words(h, m5)
            if not words:
                errors.append(f"{fmt_time(h, m5)}: no words produced")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Test 6: Word positions don't exceed grid bounds
# ═══════════════════════════════════════════════════════════════════
def test_bounds():
    errors = []
    all_positions = list(EXPECTED_MOD.values())
    for h in range(1, 13):
        all_positions.append(HOURS_GEN[h])
        all_positions.append(HOURS_NOM[h])
    for pos in all_positions:
        row, cs, ce = pos
        if row < 0 or row >= 16:
            errors.append(f"Row {row} out of bounds at {pos}")
        if cs < 0 or ce > COLS or cs >= ce:
            errors.append(f"Cols [{cs}:{ce}] invalid at {pos}")
    return errors


# ═══════════════════════════════════════════════════════════════════
#  Run all tests
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    tests = [
        ("Grid dimensions (16×16)",           test_grid_dimensions),
        ("Word positions match grid text",    test_word_positions),
        ("Word position bounds",              test_bounds),
        ("All 144 time slots covered",        test_all_slots_covered),
        ("No co-active collisions (720 times)", test_no_collisions),
        ("Reading order (720 times)",         test_reading_order),
    ]

    total_errors = 0
    for name, fn in tests:
        errors = fn()
        status = "✓ PASS" if not errors else f"✗ FAIL ({len(errors)})"
        print(f"  {status}  {name}")
        for e in errors:
            print(f"         {e}")
        total_errors += len(errors)

    print()
    if total_errors == 0:
        print("  All tests passed.")
    else:
        print(f"  {total_errors} error(s) total.")
        sys.exit(1)
