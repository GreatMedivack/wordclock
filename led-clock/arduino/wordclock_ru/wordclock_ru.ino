// Word Clock RU — ESP32-S3 + WS2812B (195 LEDs, 13×15 Cyrillic grid)
// Displays: ПЯТЬ ДН ЧЕТЫРЕ СЕМЬ (5:47 PM)

#include <FastLED.h>
#include <WiFi.h>
#include <time.h>

const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* NTP_SERVER    = "pool.ntp.org";
const long  GMT_OFFSET    = 3 * 3600;
const int   DST_OFFSET    = 0;

#define LED_PIN    48
#define COLS       15
#define ROWS       13
#define NUM_LEDS   (ROWS * COLS)  // 195
#define BRIGHTNESS 40
#define LED_TYPE   WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];
const CRGB COLOR_ON  = CRGB(255, 180, 80);
const CRGB COLOR_OFF = CRGB(0, 0, 0);

// Grid (for reference):
// 0: ОДИНЖДВАЮТРИБШП
// 1: ЧЕТЫРЕЛПЯТЬГУКМ
// 2: ШЕСТЬЖСЕМЬГДЦУХ
// 3: ВОСЕМЬХДЕВЯТЬЙШ
// 4: ДЕСЯТЬЛКМБЦУЖФХ
// 5: ОДИННАДЦАТЬГУКМ
// 6: ДВЕНАДЦАТЬДНЖНЧ
// 7: НОЛЬЖОДИНРДВАБЧ   (tens)
// 8: ТРИГЧЕТЫРЕКПЯТЬ   (tens)
// 9: НОЛЬЮОДИНМДВАВУ   (ones)
// 10: ТРИЗЧЕТЫРЕХПЯТЬ  (ones)
// 11: ШЕСТЬСЕМЬВОСЕМЬ  (ones)
// 12: ДЕВЯТЬЧАСЫЖКЛМН  (ones)

struct WordPos { uint8_t row; uint8_t col_start; uint8_t col_end; };

const WordPos HOURS[] = {
    {0, 0, 0},    // placeholder
    {0, 0, 4},    // 1: ОДИН
    {0, 5, 8},    // 2: ДВА
    {0, 9, 12},   // 3: ТРИ
    {1, 0, 6},    // 4: ЧЕТЫРЕ
    {1, 7, 11},   // 5: ПЯТЬ
    {2, 0, 5},    // 6: ШЕСТЬ
    {2, 6, 10},   // 7: СЕМЬ
    {3, 0, 6},    // 8: ВОСЕМЬ
    {3, 7, 13},   // 9: ДЕВЯТЬ
    {4, 0, 6},    // 10: ДЕСЯТЬ
    {5, 0, 11},   // 11: ОДИННАДЦАТЬ
    {6, 0, 10},   // 12: ДВЕНАДЦАТЬ
};

const WordPos AMPM_WORDS[] = {
    {6, 10, 12},  // 0: ДН (AM)
    {6, 13, 15},  // 1: НЧ (PM)
};

const WordPos TENS_WORDS[] = {
    {7, 0, 4},    // 0: НОЛЬ
    {7, 5, 9},    // 1: ОДИН
    {7, 10, 13},  // 2: ДВА
    {8, 0, 3},    // 3: ТРИ
    {8, 4, 10},   // 4: ЧЕТЫРЕ
    {8, 11, 15},  // 5: ПЯТЬ
};

const WordPos ONES_WORDS[] = {
    {9, 0, 4},    // 0: НОЛЬ
    {9, 5, 9},    // 1: ОДИН
    {9, 10, 13},  // 2: ДВА
    {10, 0, 3},   // 3: ТРИ
    {10, 4, 10},  // 4: ЧЕТЫРЕ
    {10, 11, 15}, // 5: ПЯТЬ
    {11, 0, 5},   // 6: ШЕСТЬ
    {11, 5, 9},   // 7: СЕМЬ
    {11, 9, 15},  // 8: ВОСЕМЬ
    {12, 0, 6},   // 9: ДЕВЯТЬ
};

uint16_t ledIndex(uint8_t row, uint8_t col) {
    if (row % 2 == 0) return row * COLS + col;
    return row * COLS + (COLS - 1 - col);
}

void lightWord(const WordPos& w, CRGB color) {
    for (uint8_t c = w.col_start; c < w.col_end; c++)
        leds[ledIndex(w.row, c)] = color;
}

struct ClockState { uint8_t hour12, tens, ones, is_pm; };
bool operator!=(const ClockState& a, const ClockState& b) {
    return a.hour12 != b.hour12 || a.tens != b.tens || a.ones != b.ones || a.is_pm != b.is_pm;
}

void showTime(const ClockState& st) {
    fill_solid(leds, NUM_LEDS, COLOR_OFF);
    lightWord(HOURS[st.hour12], COLOR_ON);
    lightWord(AMPM_WORDS[st.is_pm], COLOR_ON);
    lightWord(TENS_WORDS[st.tens], COLOR_ON);
    lightWord(ONES_WORDS[st.ones], COLOR_ON);
    FastLED.show();
}

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) delay(500);
}

void startupSweep() {
    for (uint16_t i = 0; i < NUM_LEDS; i++) {
        leds[i] = COLOR_ON;
        if (i > 0) leds[i - 1] = COLOR_OFF;
        FastLED.show();
        delay(10);
    }
    leds[NUM_LEDS - 1] = COLOR_OFF;
    FastLED.show();
}

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
    configTime(GMT_OFFSET, DST_OFFSET, NTP_SERVER);
    struct tm t;
    while (!getLocalTime(&t)) delay(500);
    Serial.println("Word Clock RU ready");
}

void loop() {
    struct tm t;
    if (!getLocalTime(&t)) { delay(1000); return; }

    uint8_t h24 = t.tm_hour;
    uint8_t is_pm = (h24 >= 12) ? 1 : 0;
    uint8_t h12 = h24 % 12;
    if (h12 == 0) h12 = 12;

    ClockState current = {h12, (uint8_t)(t.tm_min / 10), (uint8_t)(t.tm_min % 10), is_pm};
    if (firstRun || current != lastState) {
        showTime(current);
        lastState = current;
        firstRun = false;
    }
    delay(1000);
}
