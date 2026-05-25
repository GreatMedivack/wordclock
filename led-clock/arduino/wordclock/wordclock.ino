// Word Clock — ESP32-S3 + WS2812B (165 LEDs, 11×15 serpentine grid)
// USB 5V powered, NTP time sync over WiFi

#include <FastLED.h>
#include <WiFi.h>
#include <time.h>

// ── Configuration ──────────────────────────────────────────────────────────────

const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* NTP_SERVER    = "pool.ntp.org";
const long  GMT_OFFSET    = 3 * 3600;   // UTC+3 (Moscow), adjust for your timezone
const int   DST_OFFSET    = 0;

#define LED_PIN    48          // GPIO for WS2812B data line
#define NUM_LEDS   165         // 11 rows × 15 cols
#define BRIGHTNESS 40          // 0-255, 40 is gentle for a clock
#define LED_TYPE   WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

// Active letter color (warm white)
const CRGB COLOR_ON  = CRGB(255, 180, 80);
// Inactive letter color (off or very dim)
const CRGB COLOR_OFF = CRGB(0, 0, 0);

#define COLS 15
#define ROWS 11

// ── Letter Grid (matches the e-paper version) ─────────────────────────────────

const char GRID[ROWS][COLS + 1] = {
    "ONEXTWODTHREEIR",  // row 0
    "FOURFIVESIXHATN",  // row 1
    "SEVENREIGHTBULK",  // row 2
    "NINETENVCELEVEN",  // row 3
    "AMTWELVEXPMHOUR",  // row 4
    "ZEROXONEDTWOBIA",  // row 5
    "THREEGFOURFIVER",  // row 6
    "ZEROXONETWOIAHD",  // row 7
    "THREEFOURFIVESK",  // row 8
    "SIXSEVENEIGHTLM",  // row 9
    "NINEWORDCLOCKZX",  // row 10
};

// ── Word positions: {row, col_start, col_end} (col_end exclusive) ──────────────

struct WordPos { uint8_t row; uint8_t col_start; uint8_t col_end; };

const WordPos HOURS[] = {
    {0, 0, 0},   // placeholder for index 0
    {0, 0, 3},   // 1: ONE
    {0, 4, 7},   // 2: TWO
    {0, 8, 13},  // 3: THREE
    {1, 0, 4},   // 4: FOUR
    {1, 4, 8},   // 5: FIVE
    {1, 8, 11},  // 6: SIX
    {2, 0, 5},   // 7: SEVEN
    {2, 6, 11},  // 8: EIGHT
    {3, 0, 4},   // 9: NINE
    {3, 4, 7},   // 10: TEN
    {3, 9, 15},  // 11: ELEVEN
    {4, 2, 8},   // 12: TWELVE
};

const WordPos AMPM_WORDS[] = {
    {4, 0, 2},   // 0: AM
    {4, 9, 11},  // 1: PM
};

const WordPos TENS_WORDS[] = {
    {5, 0, 4},   // 0: ZERO
    {5, 5, 8},   // 1: ONE
    {5, 9, 12},  // 2: TWO
    {6, 0, 5},   // 3: THREE
    {6, 6, 10},  // 4: FOUR
    {6, 10, 14}, // 5: FIVE
};

const WordPos ONES_WORDS[] = {
    {7, 0, 4},   // 0: ZERO
    {7, 5, 8},   // 1: ONE
    {7, 8, 11},  // 2: TWO
    {8, 0, 5},   // 3: THREE
    {8, 5, 9},   // 4: FOUR
    {8, 9, 13},  // 5: FIVE
    {9, 0, 3},   // 6: SIX
    {9, 3, 8},   // 7: SEVEN
    {9, 8, 13},  // 8: EIGHT
    {10, 0, 4},  // 9: NINE
};

// ── LED index mapping (serpentine layout) ──────────────────────────────────────
// Row 0: left→right (LED 0..14)
// Row 1: right→left (LED 15..29)
// Row 2: left→right (LED 30..44)
// ...

uint16_t ledIndex(uint8_t row, uint8_t col) {
    if (row % 2 == 0) {
        return row * COLS + col;
    } else {
        return row * COLS + (COLS - 1 - col);
    }
}

// ── Light up a word ────────────────────────────────────────────────────────────

void lightWord(const WordPos& w, CRGB color) {
    for (uint8_t c = w.col_start; c < w.col_end; c++) {
        leds[ledIndex(w.row, c)] = color;
    }
}

// ── Set the display for a given time ───────────────────────────────────────────

struct ClockState {
    uint8_t hour12;
    uint8_t tens;
    uint8_t ones;
    uint8_t is_pm;
};

bool operator==(const ClockState& a, const ClockState& b) {
    return a.hour12 == b.hour12 && a.tens == b.tens
        && a.ones == b.ones && a.is_pm == b.is_pm;
}

bool operator!=(const ClockState& a, const ClockState& b) {
    return !(a == b);
}

void showTime(const ClockState& st) {
    fill_solid(leds, NUM_LEDS, COLOR_OFF);

    lightWord(HOURS[st.hour12], COLOR_ON);
    lightWord(AMPM_WORDS[st.is_pm], COLOR_ON);
    lightWord(TENS_WORDS[st.tens], COLOR_ON);
    lightWord(ONES_WORDS[st.ones], COLOR_ON);

    FastLED.show();
}

// ── WiFi + NTP ─────────────────────────────────────────────────────────────────

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
}

void syncTime() {
    configTime(GMT_OFFSET, DST_OFFSET, NTP_SERVER);
    struct tm t;
    while (!getLocalTime(&t)) {
        delay(500);
    }
}

// ── Startup animation ─────────────────────────────────────────────────────────

void startupSweep() {
    for (uint16_t i = 0; i < NUM_LEDS; i++) {
        leds[i] = COLOR_ON;
        if (i > 0) leds[i - 1] = COLOR_OFF;
        FastLED.show();
        delay(15);
    }
    leds[NUM_LEDS - 1] = COLOR_OFF;
    FastLED.show();
}

// ── Main ───────────────────────────────────────────────────────────────────────

ClockState lastState = {0, 0, 0, 0};
bool firstRun = true;

void setup() {
    Serial.begin(115200);

    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
    FastLED.setBrightness(BRIGHTNESS);
    fill_solid(leds, NUM_LEDS, COLOR_OFF);
    FastLED.show();

    startupSweep();

    connectWiFi();
    Serial.println("WiFi connected");

    syncTime();
    Serial.println("NTP synced");
}

void loop() {
    struct tm t;
    if (!getLocalTime(&t)) {
        delay(1000);
        return;
    }

    uint8_t h24 = t.tm_hour;
    uint8_t is_pm = (h24 >= 12) ? 1 : 0;
    uint8_t h12 = h24 % 12;
    if (h12 == 0) h12 = 12;

    ClockState current = {h12, (uint8_t)(t.tm_min / 10), (uint8_t)(t.tm_min % 10), is_pm};

    if (firstRun || current != lastState) {
        showTime(current);
        Serial.printf("%02d:%02d %s\n", h12, t.tm_min, is_pm ? "PM" : "AM");
        lastState = current;
        firstRun = false;
    }

    delay(1000);
}
