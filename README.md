# Word Clock

Kisai-style word clock that displays time on a character grid. Active words (hour, minutes, AM/PM) are highlighted with inverted colors (white on black).

![preview showing 3:47 PM](preview_4x.png)

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

- **Raspberry Pi Zero W** — BCM2835, WiFi, USB OTG
- **Waveshare 2.13" e-Paper HAT V4** — SSD1680, 250x122px, 1-bit B/W, SPI
- **PCF8523 RTC** — I2C real-time clock with battery backup (optional, falls back to system time)

## Software

- **Python 3** with Pillow for 1-bit image rendering
- **Silkscreen** pixel font (Bold, 12px)
- **Waveshare e-Paper** driver library
- **Adafruit Blinka + CircuitPython PCF8523** for RTC
- **systemd** service for autostart
- Polls every 5s, partial e-paper refresh on minute change, full refresh every 30 cycles to prevent ghosting

## Structure

```
clock.py           — main loop: poll time every 5s, render and display on change
renderer.py        — 11x15 character grid rendering to 250x122 PIL Image
epd_driver.py      — Waveshare e-Paper HAT V4 wrapper with partial/full refresh
time_source.py     — PCF8523 RTC with system time fallback
wordclock.service  — systemd unit
requirements.txt   — Python dependencies
fonts/             — Silkscreen Bold/Regular .ttf
deploy/            — SD card bootstrap scripts (prepare-sd.sh, firstboot.sh)
```

## Deploy

1. Flash Raspberry Pi OS Lite via Raspberry Pi Imager (set WiFi, SSH, hostname, user)
2. Mount SD card on desktop
3. Run `sudo ./deploy/prepare-sd.sh /media/$USER`
4. Insert SD into Pi, power on
5. First boot auto-installs dependencies and starts the clock

Alternatively, SSH into the Pi and run `./install.sh`.
