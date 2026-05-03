# Word Clock — Kisai-style E-Ink Clock for Raspberry Pi Zero W

## Context

Build a Kisai-style word clock using Raspberry Pi Zero W, Waveshare 2.13" e-paper HAT V4 (SSD1680, 250x122px, B/W), and PCF8523 RTC module. The display shows a grid of spelled-out numbers; current time is highlighted by inverting colors on the active words.

## Hardware

| Component | Details |
|-----------|---------|
| Board | Raspberry Pi Zero W |
| Display | Waveshare 2.13" e-Paper HAT V4, SSD1680, 250x122px, 1-bit B/W |
| RTC | PCF8523 via I2C |
| Power | USB micro or battery via GPIO |

## Display Concept

A fixed grid of uppercase English words (word-search style):
- **Rows 1-4**: Hours — ONE through TWELVE, packed with filler letters
- **Rows 5-6**: Minutes tens digit — ZERO through FIVE
- **Rows 7-8**: Minutes ones digit — ZERO through NINE (partial)
- **Row 9**: EIGHT, NINE (ones cont.) + AM, PM

All words always visible. Inactive words: black text on white. Active words: **white text on black rectangle** (inverted). This gives maximum contrast on B/W e-ink.

Example: 3:47 PM highlights THREE (hours), FOUR (tens), SEVEN (ones), PM.

## Architecture

### Rendering — Full re-render (Approach B)

Each minute, render the entire 250x122 1-bit image from scratch using Pillow. ~29ms on Pi Zero W — negligible at 60s intervals. No cached state, simple code.

### Grid Layout

Monospace pixel font at ~12px. Grid: ~18 chars wide x 9 rows. Each word has a fixed (row, col_start, col_end) position in the grid. Filler characters fill gaps between words.

```
Row 0: O N E S N T W O A I T H R E E I x x   (ONE, TWO, THREE)
Row 1: F O U R F I V E S I X A S E V E N x   (FOUR, FIVE, SIX, SEVEN)
Row 2: E I G H T X N I N E H T E N A P x x   (EIGHT, NINE, TEN)
Row 3: E L E V E N I H A T W E L V E I x x   (ELEVEN, TWELVE)
Row 4: Z E R O X O N E H T W O D I A S x x   (ZERO, ONE, TWO — tens)
Row 5: T H R E E I F O U R D A F I V E x x   (THREE, FOUR, FIVE — tens)
Row 6: Z E R O O N E T W O A T H R E E x x   (ZERO, ONE, TWO, THREE — ones)
Row 7: F O U R F I V E S I X A S E V E N x   (FOUR, FIVE, SIX, SEVEN — ones)
Row 8: E I G H T N I N E H A M P M O R x x   (EIGHT, NINE — ones, AM, PM)
```

Note: exact filler letters and positions will be finalized during implementation to avoid accidentally spelling number words.

### Word Position Map

```python
HOURS = {
    1:  (0, 0, 3),    # ONE     row 0, cols 0-2
    2:  (0, 5, 8),    # TWO     row 0, cols 5-7
    3:  (0, 10, 15),  # THREE   row 0, cols 10-14
    4:  (1, 0, 4),    # FOUR    row 1, cols 0-3
    5:  (1, 4, 8),    # FIVE    row 1, cols 4-7
    6:  (1, 8, 11),   # SIX     row 1, cols 8-10
    7:  (1, 12, 17),  # SEVEN   row 1, cols 12-16
    8:  (2, 0, 5),    # EIGHT   row 2, cols 0-4
    9:  (2, 6, 10),   # NINE    row 2, cols 6-9
    10: (2, 11, 14),  # TEN     row 2, cols 11-13
    11: (3, 0, 6),    # ELEVEN  row 3, cols 0-5
    12: (3, 9, 15),   # TWELVE  row 3, cols 9-14
}

TENS = {
    0: (4, 0, 4),     # ZERO
    1: (4, 5, 8),     # ONE
    2: (4, 9, 12),    # TWO
    3: (5, 0, 5),     # THREE
    4: (5, 6, 10),    # FOUR
    5: (5, 12, 16),   # FIVE
}

ONES = {
    0: (6, 0, 4),     # ZERO
    1: (6, 4, 7),     # ONE
    2: (6, 7, 10),    # TWO
    3: (6, 11, 16),   # THREE
    4: (7, 0, 4),     # FOUR
    5: (7, 4, 8),     # FIVE
    6: (7, 8, 11),    # SIX
    7: (7, 12, 17),   # SEVEN
    8: (8, 0, 5),     # EIGHT
    9: (8, 5, 9),     # NINE
}

AMPM = {
    'AM': (8, 10, 12),
    'PM': (8, 12, 14),
}
```

### File Structure

```
clock/
  clock.py           # Main loop: RTC read, render, display
  renderer.py        # Grid definition (word positions), render function
  epd_driver.py      # Wrapper around waveshare_epd.epd2in13_V4
  fonts/             # Bundled pixel font (Silkscreen or Press Start 2P)
  install.sh         # apt/pip deps + systemd setup
  wordclock.service  # systemd unit file
  requirements.txt   # Python dependencies
```

### Dependencies

```
waveshare-epd        # pip or vendored from Waveshare GitHub
adafruit-circuitpython-pcf8523
adafruit-blinka
Pillow
RPi.GPIO
spidev
```

## E-Paper Driver

```python
from waveshare_epd import epd2in13_V4

epd = epd2in13_V4.EPD()
epd.init()
epd.Clear()

# Image size: (epd.height, epd.width) = (250, 122)
# Create Pillow Image at (250, 122) in '1' mode

# First frame:
epd.displayPartBaseImage(epd.getbuffer(image))

# Each subsequent minute:
epd.displayPartial(epd.getbuffer(image))

# Every 30 minutes (full refresh to clear ghosting):
epd.display(epd.getbuffer(image))

# On shutdown:
epd.sleep()
```

## RTC

```python
import board
import adafruit_pcf8523

i2c = board.I2C()
rtc = adafruit_pcf8523.PCF8523(i2c)
t = rtc.datetime  # struct_time
```

## Main Loop

```
1. Init e-paper (epd.init, epd.Clear)
2. Init RTC (I2C)
3. Render first frame -> displayPartBaseImage()
4. refresh_counter = 0
5. Loop forever:
   a. Sleep until next minute boundary (60 - current_seconds)
   b. Read rtc.datetime
   c. Convert to 12h: hour_12, ampm_str
   d. tens_digit = minute // 10
   e. ones_digit = minute % 10
   f. Render image with highlights: hour_12, tens_digit, ones_digit, ampm_str
   g. refresh_counter += 1
   h. If refresh_counter >= 30:
        epd.display(full_refresh) + displayPartBaseImage()
        refresh_counter = 0
      Else:
        epd.displayPartial()
6. On SIGTERM/SIGINT: epd.sleep(), sys.exit(0)
```

## Rendering Function

```python
def render(hour, tens, ones, ampm):
    img = Image.new('1', (250, 122), 255)  # white background
    draw = ImageDraw.Draw(img)
    
    active_words = [
        HOURS[hour],
        TENS[tens],
        ONES[ones],
        AMPM[ampm],
    ]
    
    for row_idx, row_text in enumerate(GRID):
        for col_idx, char in enumerate(row_text):
            x = LEFT_MARGIN + col_idx * CHAR_WIDTH
            y = TOP_MARGIN + row_idx * ROW_HEIGHT
            
            if is_active(row_idx, col_idx, active_words):
                # Inverted: white text on black rect
                draw.rectangle([x, y, x+CHAR_WIDTH, y+ROW_HEIGHT], fill=0)
                draw.text((x, y), char, font=font, fill=255)
            else:
                # Normal: black text on white
                draw.text((x, y), char, font=font, fill=0)
    
    return img
```

## Systemd Service

```ini
[Unit]
Description=Word Clock E-Ink Display
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/clock/clock.py
WorkingDirectory=/home/pi/clock
Restart=on-failure
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
```

Root is required for SPI/GPIO access.

## Verification

1. Run `python3 clock.py` on the Pi — display should show the word grid with current time highlighted
2. Wait 1+ minutes — display should update via partial refresh without flicker
3. Wait 30+ minutes — one full refresh should occur (brief flicker, then clean image)
4. Kill the process (Ctrl+C) — display should remain showing last time (e-ink retains image)
5. Reboot Pi — systemd should auto-start the clock
6. Check `systemctl status wordclock` — should show active/running
