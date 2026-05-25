# LED Word Clock

Backlit word clock with a 15×11 letter grid and individually addressable WS2812B LEDs. Active letters glow warm white to spell the current time; the rest stay dark behind a black vinyl mask.

Same letter grid as the [e-paper version](../README.md), adapted for physical LED backlighting.

```
O N E  T W O  T H R E E
F O U R  F I V E  S I X
S E V E N  E I G H T
N I N E  T E N  E L E V E N
A M  T W E L V E  P M  HOUR
ZERO  ONE  TWO
THREE  FOUR  FIVE
ZERO  ONE  TWO
THREE  FOUR  FIVE
SIX  SEVEN  EIGHT
NINE  WORD  CLOCK
```

## Hardware

### Electronics

| Component | Spec | ~Price |
|-----------|------|--------|
| ESP32-S3 DevKit | WiFi, USB-C, 1× GPIO for LED data | $6 |
| WS2812B LED strip | 60 LED/m, 5V, cut to 15 per row, 11 rows (165 total) | $8 |
| USB-C cable + 5V 2A adapter | Powers both ESP32 and LEDs | $5 |

Total electronics: **~$19**

### Physical

| Component | Spec | ~Price |
|-----------|------|--------|
| Back panel | 4mm plywood or black PVC, sized to grid | $3 |
| Baffle grid | 3D-printed or laser-cut cardboard dividers, 10–15mm tall | $3 |
| Diffuser | 2–3mm opal/frosted acrylic sheet | $5 |
| Front face | Black vinyl with letter cutouts (Cricut/laser) | $3 |
| Frame | Wood, aluminum, or 3D-printed edge strip | $5 |

Total physical: **~$19**

### Sizes

| Variant | Cell size | Overall | Notes |
|---------|-----------|---------|-------|
| Desktop | 12mm | 180 × 132mm | Fits on a desk with kickstand |
| Wall | 25mm | 375 × 275mm | Readable from 3–5m |
| Large wall | 35mm | 525 × 385mm | Statement piece |

## Wiring

### LED strip layout (serpentine)

The LED strip is arranged in a snake pattern, starting from the **top-left** corner:

```
Row  0: → LED   0   1   2   3   4   5   6   7   8   9  10  11  12  13  14
Row  1: ← LED  29  28  27  26  25  24  23  22  21  20  19  18  17  16  15
Row  2: → LED  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44
Row  3: ← LED  59  58  57  56  55  54  53  52  51  50  49  48  47  46  45
Row  4: → LED  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74
Row  5: ← LED  89  88  87  86  85  84  83  82  81  80  79  78  77  76  75
Row  6: → LED  90  91  92  93  94  95  96  97  98  99 100 101 102 103 104
Row  7: ← LED 119 118 117 116 115 114 113 112 111 110 109 108 107 106 105
Row  8: → LED 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134
Row  9: ← LED 149 148 147 146 145 144 143 142 141 140 139 138 137 136 135
Row 10: → LED 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164
```

### ESP32 connections

```
ESP32-S3 DevKit          WS2812B strip
─────────────────        ─────────────
GPIO 48  ──────────────→ DIN (data in)
5V (USB) ──────────────→ +5V
GND      ──────────────→ GND
```

**Important:**
- Add a 330–470Ω resistor on the data line (GPIO 48 → DIN)
- Add a 1000µF capacitor across +5V and GND near the first LED
- If LED strip draws >500mA, power it directly from the USB adapter, not through the ESP32 — share GND only

## Assembly

```
┌─────────────────────────────┐
│  1. Back panel (plywood)    │  ← LED strip glued here, serpentine
│  2. WS2812B strip           │
│  3. Baffle grid             │  ← dividers prevent light bleed
│  4. Diffuser (frosted acrylic) │  ← softens LED point source
│  5. Vinyl mask (black + letter cutouts) │
│  6. Frame                   │
└─────────────────────────────┘
```

Cross-section view:

```
          ┌── frame ──────────────────────────┐
          │  ┌── vinyl mask (letters) ────┐   │
          │  │  ┌── diffuser ──────────┐  │   │
    light │  │  │                      │  │   │
    ←←←←← │  │  │  ┌── baffle walls ┐ │  │   │
          │  │  │  │  ░░ LED ░░      │ │  │   │
          │  │  │  └─────────────────┘ │  │   │
          │  │  └──────────────────────┘  │   │
          │  └────────────────────────────┘   │
          │         back panel                │
          └───────────────────────────────────┘
```

## Firmware

Two options — pick one:

### Arduino (recommended for stability)

1. Install [Arduino IDE](https://www.arduino.cc/en/software) or PlatformIO
2. Add ESP32 board support (Espressif Arduino core)
3. Install **FastLED** library
4. Open `arduino/wordclock/wordclock.ino`
5. Set `WIFI_SSID`, `WIFI_PASSWORD`, `GMT_OFFSET`
6. Set `LED_PIN` if using a different GPIO
7. Upload to ESP32-S3

### MicroPython

1. Flash [MicroPython for ESP32-S3](https://micropython.org/download/ESP32_GENERIC_S3/)
2. Copy `micropython/boot.py` and `micropython/main.py` to the board
3. Edit WiFi credentials and `UTC_OFFSET` in `main.py`

## Tools

### Grid visualizer

```bash
# Show grid with highlighted time
python tools/grid_visualizer.py --time "5:27 PM"

# Show LED index wiring map
python tools/grid_visualizer.py --wiring

# Generate SVG cutting template for baffles
python tools/grid_visualizer.py --svg --cell 25
```

### Vinyl face template

```bash
# Wall clock (25mm cells)
python tools/vinyl_template.py --cell 25

# Desktop (12mm cells)
python tools/vinyl_template.py --cell 12

# Large wall (35mm cells)
python tools/vinyl_template.py --cell 35
```

Produces SVG files with black rectangles and letter-shaped cutouts — send directly to a Cricut/Silhouette plotter or laser cutter.

## Power budget

| Brightness | Current (165 LEDs) | USB adapter |
|-----------|-------------------|-------------|
| 10% | ~0.3A | Any USB |
| 25% | ~0.8A | 1A USB |
| 50% | ~1.5A | 2A USB |
| 100% | ~3A | 5V 3A dedicated |

At 15–25% brightness (comfortable for a clock), a standard 2A USB adapter works fine.
