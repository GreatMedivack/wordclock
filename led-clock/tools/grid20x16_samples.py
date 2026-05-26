#!/usr/bin/env python3
"""Generate 20 text mockups for the 20×16 Russian word clock grid."""

GRID = [
    "ОДИНЖДВАКТРИБШПГ",  #  0: H1:ОДИН H2:ДВА H3:ТРИ
    "ЧЕТЫРЕЖПЯТЬКБШПГ",  #  1: H4:ЧЕТЫРЕ H5:ПЯТЬ
    "ШЕСТЬЖСЕМЬКБШПГУ",  #  2: H6:ШЕСТЬ H7:СЕМЬ
    "ВОСЕМЬЖДЕВЯТЬКБШ",  #  3: H8:ВОСЕМЬ H9:ДЕВЯТЬ
    "ДЕСЯТЬЖКБШПГУЦХР",  #  4: H10:ДЕСЯТЬ
    "ОДИННАДЦАТЬЖКБШП",  #  5: H11:ОДИННАДЦАТЬ
    "ДВЕНАДЦАТЬЖКБШПГ",  #  6: H12:ДВЕНАДЦАТЬ
    "ДВАДЦАТЬТРИДЦАТЬ",  #  7: T20:ДВАДЦАТЬ T30:ТРИДЦАТЬ
    "СОРОКЖПЯТЬДЕСЯТК",  #  8: T40:СОРОК T50:ПЯТЬДЕСЯТ
    "ДЕСЯТЬЖДЕВЯТЬКБШ",  #  9: M10:ДЕСЯТЬ U9:ДЕВЯТЬ
    "ОДИННАДЦАТЬЖСЕМЬ",  # 10: M11:ОДИННАДЦАТЬ U7:СЕМЬ
    "ДВЕНАДЦАТЬЖШЕСТЬ",  # 11: M12:ДВЕНАДЦАТЬ U6:ШЕСТЬ
    "ТРИНАДЦАТЬЖПЯТЬК",  # 12: M13:ТРИНАДЦАТЬ U5:ПЯТЬ
    "ЧЕТЫРНАДЦАТЬЖТРИ",  # 13: M14:ЧЕТЫРНАДЦАТЬ U3:ТРИ
    "ПЯТНАДЦАТЬЖДВЕКБ",  # 14: M15:ПЯТНАДЦАТЬ U2:ДВЕ
    "ШЕСТНАДЦАТЬЖОДНА",  # 15: M16:ШЕСТНАДЦАТЬ U1:ОДНА
    "СЕМНАДЦАТЬЖНОЛЬК",  # 16: M17:СЕМНАДЦАТЬ U0:НОЛЬ
    "ВОСЕМНАДЦАТЬЖКБШ",  # 17: M18:ВОСЕМНАДЦАТЬ
    "ДЕВЯТНАДЦАТЬЖКБШ",  # 18: M19:ДЕВЯТНАДЦАТЬ
    "ВОСЕМЬЖЧЕТЫРЕКБШ",  # 19: U8:ВОСЕМЬ U4:ЧЕТЫРЕ
]

COLS = 16
ROWS = 20

HOURS = {
    1:  (0, 0, 4),    2:  (0, 5, 8),    3:  (0, 9, 12),
    4:  (1, 0, 6),    5:  (1, 7, 11),   6:  (2, 0, 5),
    7:  (2, 6, 10),   8:  (3, 0, 6),    9:  (3, 7, 13),
    10: (4, 0, 6),    11: (5, 0, 11),   12: (6, 0, 10),
}

TEENS = {
    10: (9, 0, 6),     11: (10, 0, 11),  12: (11, 0, 10),
    13: (12, 0, 10),   14: (13, 0, 12),  15: (14, 0, 10),
    16: (15, 0, 11),   17: (16, 0, 10),  18: (17, 0, 12),
    19: (18, 0, 12),
}

TENS = {
    20: (7, 0, 8),   30: (7, 8, 16),
    40: (8, 0, 5),   50: (8, 6, 15),
}

UNITS = {
    0: (16, 11, 15),   1: (15, 12, 16),  2: (14, 11, 14),
    3: (13, 13, 16),   4: (19, 7, 13),   5: (12, 11, 15),
    6: (11, 11, 16),   7: (10, 12, 16),  8: (19, 0, 6),
    9: (9, 7, 13),
}


def active_positions(hour12, minute):
    active = set()

    row, cs, ce = HOURS[hour12]
    for c in range(cs, ce):
        active.add((row, c))

    if minute == 0:
        return active

    if 1 <= minute <= 9:
        # НОЛЬ + unit
        row, cs, ce = UNITS[0]
        for c in range(cs, ce):
            active.add((row, c))
        row, cs, ce = UNITS[minute]
        for c in range(cs, ce):
            active.add((row, c))
    elif 10 <= minute <= 19:
        row, cs, ce = TEENS[minute]
        for c in range(cs, ce):
            active.add((row, c))
    else:
        tens_val = (minute // 10) * 10
        ones_val = minute % 10
        row, cs, ce = TENS[tens_val]
        for c in range(cs, ce):
            active.add((row, c))
        if ones_val > 0:
            row, cs, ce = UNITS[ones_val]
            for c in range(cs, ce):
                active.add((row, c))

    return active


def describe_time(hour12, minute):
    h_names = {
        1: "ОДИН", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ",
        6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ", 10: "ДЕСЯТЬ",
        11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
    }
    parts = [h_names[hour12]]
    if minute == 0:
        pass
    elif 1 <= minute <= 9:
        u_names = {
            0: "НОЛЬ", 1: "ОДНА", 2: "ДВЕ", 3: "ТРИ", 4: "ЧЕТЫРЕ",
            5: "ПЯТЬ", 6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ",
        }
        parts.append("НОЛЬ")
        parts.append(u_names[minute])
    elif 10 <= minute <= 19:
        t_names = {
            10: "ДЕСЯТЬ", 11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
            13: "ТРИНАДЦАТЬ", 14: "ЧЕТЫРНАДЦАТЬ", 15: "ПЯТНАДЦАТЬ",
            16: "ШЕСТНАДЦАТЬ", 17: "СЕМНАДЦАТЬ", 18: "ВОСЕМНАДЦАТЬ",
            19: "ДЕВЯТНАДЦАТЬ",
        }
        parts.append(t_names[minute])
    else:
        tens_names = {20: "ДВАДЦАТЬ", 30: "ТРИДЦАТЬ", 40: "СОРОК", 50: "ПЯТЬДЕСЯТ"}
        u_names = {
            1: "ОДНА", 2: "ДВЕ", 3: "ТРИ", 4: "ЧЕТЫРЕ",
            5: "ПЯТЬ", 6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ",
        }
        tens_val = (minute // 10) * 10
        ones_val = minute % 10
        parts.append(tens_names[tens_val])
        if ones_val > 0:
            parts.append(u_names[ones_val])
    return " ".join(parts)


def render_text(hour12, minute):
    active = active_positions(hour12, minute)
    lines = []
    for row_idx, row_text in enumerate(GRID):
        chars = []
        for col_idx, ch in enumerate(row_text):
            if (row_idx, col_idx) in active:
                chars.append(f"\033[97;40m {ch} \033[0m")
            else:
                chars.append(f"\033[90m {ch} \033[0m")
        lines.append("".join(chars))
    return "\n".join(lines)


def render_text_plain(hour12, minute):
    active = active_positions(hour12, minute)
    lines = []
    for row_idx, row_text in enumerate(GRID):
        chars = []
        for col_idx, ch in enumerate(row_text):
            if (row_idx, col_idx) in active:
                chars.append(f"[{ch}]")
            else:
                chars.append(f" {ch} ")
        lines.append("".join(chars))
    return "\n".join(lines)


# Validate grid dimensions
errors = 0
for i, row in enumerate(GRID):
    if len(row) != COLS:
        print(f"ERROR: row {i} has {len(row)} chars, expected {COLS}")
        errors += 1

# Validate all word extractions
print("=== WORD VALIDATION ===\n")

h_exp = {
    1: "ОДИН", 2: "ДВА", 3: "ТРИ", 4: "ЧЕТЫРЕ", 5: "ПЯТЬ",
    6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ", 10: "ДЕСЯТЬ",
    11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
}
for k, (r, cs, ce) in HOURS.items():
    word = GRID[r][cs:ce]
    ok = "✓" if word == h_exp[k] else f"✗ got '{word}'"
    print(f"  H{k:>2}: {h_exp[k]:>12} = row {r:>2} [{cs:>2}:{ce:>2}] → '{word}' {ok}")
    if word != h_exp[k]:
        errors += 1

t_exp = {
    10: "ДЕСЯТЬ", 11: "ОДИННАДЦАТЬ", 12: "ДВЕНАДЦАТЬ",
    13: "ТРИНАДЦАТЬ", 14: "ЧЕТЫРНАДЦАТЬ", 15: "ПЯТНАДЦАТЬ",
    16: "ШЕСТНАДЦАТЬ", 17: "СЕМНАДЦАТЬ", 18: "ВОСЕМНАДЦАТЬ",
    19: "ДЕВЯТНАДЦАТЬ",
}
for k, (r, cs, ce) in TEENS.items():
    word = GRID[r][cs:ce]
    ok = "✓" if word == t_exp[k] else f"✗ got '{word}'"
    print(f"  M{k:>2}: {t_exp[k]:>14} = row {r:>2} [{cs:>2}:{ce:>2}] → '{word}' {ok}")
    if word != t_exp[k]:
        errors += 1

tens_exp = {20: "ДВАДЦАТЬ", 30: "ТРИДЦАТЬ", 40: "СОРОК", 50: "ПЯТЬДЕСЯТ"}
for k, (r, cs, ce) in TENS.items():
    word = GRID[r][cs:ce]
    ok = "✓" if word == tens_exp[k] else f"✗ got '{word}'"
    print(f"  T{k:>2}: {tens_exp[k]:>10} = row {r:>2} [{cs:>2}:{ce:>2}] → '{word}' {ok}")
    if word != tens_exp[k]:
        errors += 1

u_exp = {
    0: "НОЛЬ", 1: "ОДНА", 2: "ДВЕ", 3: "ТРИ", 4: "ЧЕТЫРЕ",
    5: "ПЯТЬ", 6: "ШЕСТЬ", 7: "СЕМЬ", 8: "ВОСЕМЬ", 9: "ДЕВЯТЬ",
}
for k, (r, cs, ce) in UNITS.items():
    word = GRID[r][cs:ce]
    ok = "✓" if word == u_exp[k] else f"✗ got '{word}'"
    print(f"  U{k}: {u_exp[k]:>8} = row {r:>2} [{cs:>2}:{ce:>2}] → '{word}' {ok}")
    if word != u_exp[k]:
        errors += 1

if errors:
    print(f"\n{errors} ОШИБОК!")
    exit(1)

print(f"\n✓ Сетка ОК: {ROWS}×{COLS} = {ROWS * COLS} ячеек, все слова верны\n")

# Verify full coverage: all 720 times
print("=== COVERAGE CHECK ===\n")
for h in range(1, 13):
    for m in range(60):
        try:
            pos = active_positions(h, m)
            assert len(pos) > 0
        except Exception as e:
            print(f"  FAIL: {h}:{m:02d} — {e}")
            errors += 1
if errors:
    print(f"  {errors} failures!")
    exit(1)
print("  ✓ All 720 time variants (12h × 60min) covered\n")

# 20 samples
SAMPLES = [
    (12, 0),   (1, 0),    (7, 1),    (3, 5),    (5, 9),
    (8, 10),   (11, 11),  (2, 15),   (6, 17),   (4, 19),
    (9, 20),   (7, 21),   (10, 25),  (12, 30),  (1, 33),
    (3, 40),   (8, 42),   (5, 50),   (11, 55),  (6, 59),
]

print("=" * 60)
print("  20×16 WORD CLOCK — 20 SAMPLE TIMES")
print("=" * 60)

for i, (h, m) in enumerate(SAMPLES, 1):
    desc = describe_time(h, m)
    print(f"\n{'─' * 60}")
    print(f"  #{i:>2}  {h}:{m:02d}  →  {desc}")
    print(f"{'─' * 60}\n")
    print(render_text(h, m))
