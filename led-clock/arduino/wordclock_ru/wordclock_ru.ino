// Word Clock RU v2 — ESP32-S3 + WS2812B (260 LEDs: 16×16 grid + 4 dots)
// Natural Russian speech: ЧЕТВЕРТЬ ВОСЬМОГО, БЕЗ ДЕСЯТИ ТРИ
// Nearest-5 rounding with ±2 dot indicators (left pair = minus, right pair = plus)

#include <FastLED.h>
#include <WiFi.h>
#include <time.h>

const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* NTP_SERVER    = "pool.ntp.org";
const long  GMT_OFFSET    = 3 * 3600;  // MSK (UTC+3)
const int   DST_OFFSET    = 0;

#define LED_PIN     48
#define COLS        16
#define ROWS        16
#define GRID_LEDS   (ROWS * COLS)  // 256
#define DOT_LEDS    4
#define NUM_LEDS    (GRID_LEDS + DOT_LEDS)  // 260
#define BRIGHTNESS  40
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

// Dot LED indices (4 LEDs after the grid, centered below)
#define DOT_1  256
#define DOT_2  257
#define DOT_3  258
#define DOT_4  259

CRGB leds[NUM_LEDS];
const CRGB COLOR_ON  = CRGB(255, 180, 80);
const CRGB COLOR_OFF = CRGB(0, 0, 0);

// Grid 16×16 v4 (zero reading order issues, separate NOM_5/NOM_10):
//  0: ГДВАДЦАТЬГПЯТЬГЖ   ДВАДЦАТЬ _ ПЯТЬ_M
//  1: ЖГДЕСЯТЬГМИНУТГЖ   ДЕСЯТЬ_M _ МИНУТ
//  2: ЧЕТВЕРТЬПОЛОВИНА   ЧЕТВЕРТЬ ПОЛОВИНА
//  3: ГБЕЗГДВАДЦАТИГЖГ   БЕЗ _ ДВАДЦАТИ
//  4: ПЯТИГЧЕТВЕРТИГГГ   ПЯТИ _ ЧЕТВЕРТИ
//  5: ДЕСЯТИПЕРВОГОТРИ   ДЕСЯТИ ПЕРВОГО ТРИ
//  6: ВТОРОГОПЯТОГОЧАС   ВТОРОГО ПЯТОГО ЧАС
//  7: ТРЕТЬЕГОШЕСТОГОГ   ТРЕТЬЕГО ШЕСТОГО
//  8: ЧЕТВЁРТОГОЧЕТЫРЕ   ЧЕТВЁРТОГО ЧЕТЫРЕ
//  9: СЕДЬМОГОВОСЬМОГО   СЕДЬМОГО ВОСЬМОГО
// 10: ДЕВЯТОГОДЕСЯТОГО   ДЕВЯТОГО ДЕСЯТОГО
// 11: ОДИННАДЦАТОГОДВА   ОДИННАДЦАТОГО ДВА
// 12: ДВЕНАДЦАТОГОПЯТЬ   ДВЕНАДЦАТОГО ПЯТЬ
// 13: ДВЕНАДЦАТЬДЕСЯТЬ   ДВЕНАДЦАТЬ ДЕСЯТЬ
// 14: ОДИННАДЦАТЬШЕСТЬ   ОДИННАДЦАТЬ ШЕСТЬ
// 15: СЕМЬВОСЕМЬДЕВЯТЬ   СЕМЬ ВОСЕМЬ ДЕВЯТЬ
// Dots: LED 256-259 — left pair (minus), right pair (plus), ±2 minutes

struct WordPos { uint8_t row; uint8_t col_start; uint8_t col_end; };

// ── Minute/modifier words (rows 0-5) ──
const WordPos W_DVADTSAT  = {0,  1,  9};  // ДВАДЦАТЬ
const WordPos W_PYAT      = {0, 10, 14};  // ПЯТЬ (minute)
const WordPos W_DESYAT    = {1,  2,  8};  // ДЕСЯТЬ (minute)
const WordPos W_MINUT     = {1,  9, 14};  // МИНУТ
const WordPos W_CHETVERT  = {2,  0,  8};  // ЧЕТВЕРТЬ
const WordPos W_POLOVINA  = {2,  8, 16};  // ПОЛОВИНА
const WordPos W_BEZ       = {3,  1,  4};  // БЕЗ
const WordPos W_DVADTSATI = {3,  5, 13};  // ДВАДЦАТИ
const WordPos W_PYATI     = {4,  0,  4};  // ПЯТИ
const WordPos W_DESYATI   = {5,  0,  6};  // ДЕСЯТИ
const WordPos W_CHETVERTI = {4,  5, 13};  // ЧЕТВЕРТИ

// ── Genitive hours (for :05-:30 — "X минут СЛЕДУЮЩЕГО") ──
const WordPos HOURS_GEN[] = {
    {0, 0, 0},       // placeholder
    { 5,  6, 13},    //  1: ПЕРВОГО
    { 6,  0,  7},    //  2: ВТОРОГО
    { 7,  0,  8},    //  3: ТРЕТЬЕГО
    { 8,  0, 10},    //  4: ЧЕТВЁРТОГО
    { 6,  7, 13},    //  5: ПЯТОГО
    { 7,  8, 15},    //  6: ШЕСТОГО
    { 9,  0,  8},    //  7: СЕДЬМОГО
    { 9,  8, 16},    //  8: ВОСЬМОГО
    {10,  0,  8},    //  9: ДЕВЯТОГО
    {10,  8, 16},    // 10: ДЕСЯТОГО
    {11,  0, 13},    // 11: ОДИННАДЦАТОГО
    {12,  0, 12},    // 12: ДВЕНАДЦАТОГО
};

// ── Nominative hours (for :00 and :35-:55 — "без X ЧАС") ──
const WordPos HOURS_NOM[] = {
    {0, 0, 0},       // placeholder
    { 6, 13, 16},    //  1: ЧАС
    {11, 13, 16},    //  2: ДВА
    { 5, 13, 16},    //  3: ТРИ
    { 8, 10, 16},    //  4: ЧЕТЫРЕ
    {12, 12, 16},    //  5: ПЯТЬ
    {14, 11, 16},    //  6: ШЕСТЬ
    {15,  0,  4},    //  7: СЕМЬ
    {15,  4, 10},    //  8: ВОСЕМЬ
    {15, 10, 16},    //  9: ДЕВЯТЬ
    {13, 10, 16},    // 10: ДЕСЯТЬ
    {14,  0, 11},    // 11: ОДИННАДЦАТЬ
    {13,  0, 10},    // 12: ДВЕНАДЦАТЬ
};

uint16_t ledIndex(uint8_t row, uint8_t col) {
    // Serpentine: even rows L→R, odd rows R→L
    if (row % 2 == 0) return row * COLS + col;
    return row * COLS + (COLS - 1 - col);
}

void lightWord(const WordPos& w, CRGB color) {
    for (uint8_t c = w.col_start; c < w.col_end; c++)
        leds[ledIndex(w.row, c)] = color;
}

uint8_t nextHour(uint8_t h) {
    return h % 12 + 1;
}

struct ClockState { uint8_t hour12; uint8_t minute; };
bool operator!=(const ClockState& a, const ClockState& b) {
    return a.hour12 != b.hour12 || a.minute != b.minute;
}

void showDots(uint8_t minus_dots, uint8_t plus_dots) {
    // Left pair (DOT_1, DOT_2) = minus, filled from center outward
    if (minus_dots >= 1) leds[DOT_2] = COLOR_ON;
    if (minus_dots >= 2) leds[DOT_1] = COLOR_ON;
    // Right pair (DOT_3, DOT_4) = plus, filled from center outward
    if (plus_dots >= 1)  leds[DOT_3] = COLOR_ON;
    if (plus_dots >= 2)  leds[DOT_4] = COLOR_ON;
}

void showTime(const ClockState& st) {
    fill_solid(leds, NUM_LEDS, COLOR_OFF);

    uint8_t remainder = st.minute % 5;
    uint8_t m, plus_dots, minus_dots;
    uint8_t h = st.hour12;

    if (remainder <= 2) {
        m = (st.minute / 5) * 5;
        plus_dots = remainder;
        minus_dots = 0;
    } else {
        m = (st.minute / 5) * 5 + 5;
        minus_dots = 5 - remainder;
        plus_dots = 0;
    }

    if (m == 60) {
        m = 0;
        h = nextHour(h);
    }

    uint8_t nh = nextHour(h);

    if (m == 0) {
        lightWord(HOURS_NOM[h], COLOR_ON);
    } else if (m <= 30) {
        switch (m) {
            case 5:
                lightWord(W_PYAT, COLOR_ON);
                lightWord(W_MINUT, COLOR_ON);
                break;
            case 10:
                lightWord(W_DESYAT, COLOR_ON);
                lightWord(W_MINUT, COLOR_ON);
                break;
            case 15:
                lightWord(W_CHETVERT, COLOR_ON);
                break;
            case 20:
                lightWord(W_DVADTSAT, COLOR_ON);
                lightWord(W_MINUT, COLOR_ON);
                break;
            case 25:
                lightWord(W_DVADTSAT, COLOR_ON);
                lightWord(W_PYAT, COLOR_ON);
                lightWord(W_MINUT, COLOR_ON);
                break;
            case 30:
                lightWord(W_POLOVINA, COLOR_ON);
                break;
        }
        lightWord(HOURS_GEN[nh], COLOR_ON);
    } else {
        lightWord(W_BEZ, COLOR_ON);
        uint8_t to_min = 60 - m;
        switch (to_min) {
            case 25:
                lightWord(W_DVADTSATI, COLOR_ON);
                lightWord(W_PYATI, COLOR_ON);
                break;
            case 20:
                lightWord(W_DVADTSATI, COLOR_ON);
                break;
            case 15:
                lightWord(W_CHETVERTI, COLOR_ON);
                break;
            case 10:
                lightWord(W_DESYATI, COLOR_ON);
                break;
            case 5:
                lightWord(W_PYATI, COLOR_ON);
                break;
        }
        lightWord(HOURS_NOM[nh], COLOR_ON);
    }

    showDots(minus_dots, plus_dots);
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
        delay(8);
    }
    leds[NUM_LEDS - 1] = COLOR_OFF;
    FastLED.show();
}

ClockState lastState = {0, 0};
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
    Serial.println("Word Clock RU v2 ready");
}

void loop() {
    struct tm t;
    if (!getLocalTime(&t)) { delay(1000); return; }

    uint8_t h12 = t.tm_hour % 12;
    if (h12 == 0) h12 = 12;

    ClockState current = {h12, t.tm_min};
    if (firstRun || current != lastState) {
        showTime(current);
        lastState = current;
        firstRun = false;
    }
    delay(1000);
}
