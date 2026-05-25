"""Word Clock — ESP32-S3 + WS2812B
MicroPython firmware with language selection (EN/RU/JA).
USB 5V powered, NTP time sync over WiFi.
"""

import machine
import neopixel
import network
import ntptime
import time

# ── Configuration ───────────────────────────────────────────────────────────────

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
NTP_HOST = "pool.ntp.org"
UTC_OFFSET = 3  # hours from UTC

LED_PIN = 48
BRIGHTNESS = 0.15  # 0.0–1.0

# Language: "en", "ru", or "ja"
LANGUAGE = "en"

# Warm white
COLOR_ON = (255, 180, 80)
COLOR_OFF = (0, 0, 0)

# ── Load language grid ──────────────────────────────────────────────────────────

if LANGUAGE == "ru":
    from lang.grid_ru import GRID, COLS, ROWS, HOURS, AMPM, TENS, ONES, FIXED
elif LANGUAGE == "ja":
    from lang.grid_ja import GRID, COLS, ROWS, HOURS, AMPM, TENS, ONES, FIXED
else:
    from lang.grid_en import GRID, COLS, ROWS, HOURS, AMPM, TENS, ONES, FIXED

NUM_LEDS = ROWS * COLS


def led_index(row, col):
    if row % 2 == 0:
        return row * COLS + col
    return row * COLS + (COLS - 1 - col)


def _scale(color):
    return tuple(int(c * BRIGHTNESS) for c in color)


# ── Display ─────────────────────────────────────────────────────────────────────

np = neopixel.NeoPixel(machine.Pin(LED_PIN), NUM_LEDS)


def light_word(word_pos, color):
    row, col_start, col_end = word_pos
    c = _scale(color)
    for col in range(col_start, col_end):
        np[led_index(row, col)] = c


def show_time(hour12, tens, ones, ampm_str):
    for i in range(NUM_LEDS):
        np[i] = COLOR_OFF

    light_word(HOURS[hour12], COLOR_ON)
    light_word(AMPM[ampm_str], COLOR_ON)
    light_word(TENS[tens], COLOR_ON)
    light_word(ONES[ones], COLOR_ON)

    for pos in FIXED:
        light_word(pos, COLOR_ON)

    np.write()


# ── WiFi + NTP ──────────────────────────────────────────────────────────────────

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(40):
        if wlan.isconnected():
            print("WiFi:", wlan.ifconfig()[0])
            return
        time.sleep(0.5)
    print("WiFi connection failed")


def sync_ntp():
    ntptime.host = NTP_HOST
    for attempt in range(5):
        try:
            ntptime.settime()
            print("NTP synced")
            return
        except OSError:
            time.sleep(2)
    print("NTP sync failed")


def local_time():
    return time.localtime(time.time() + UTC_OFFSET * 3600)


# ── Startup animation ──────────────────────────────────────────────────────────

def startup_sweep():
    c = _scale(COLOR_ON)
    for i in range(NUM_LEDS):
        np[i] = c
        if i > 0:
            np[i - 1] = COLOR_OFF
        np.write()
        time.sleep_ms(15)
    np[NUM_LEDS - 1] = COLOR_OFF
    np.write()


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print(f"Word Clock [{LANGUAGE.upper()}] — {ROWS}x{COLS} = {NUM_LEDS} LEDs")

    for i in range(NUM_LEDS):
        np[i] = COLOR_OFF
    np.write()

    startup_sweep()
    connect_wifi()
    sync_ntp()

    last_key = None
    ntp_counter = 0

    while True:
        t = local_time()
        h24 = t[3]
        minute = t[4]

        ampm = "AM" if h24 < 12 else "PM"
        h12 = h24 % 12
        if h12 == 0:
            h12 = 12

        tens = minute // 10
        ones = minute % 10
        key = (h12, tens, ones, ampm)

        if key != last_key:
            show_time(h12, tens, ones, ampm)
            print(f"{h12}:{minute:02d} {ampm}")
            last_key = key

        time.sleep(1)

        ntp_counter += 1
        if ntp_counter >= 21600:
            sync_ntp()
            ntp_counter = 0


main()
