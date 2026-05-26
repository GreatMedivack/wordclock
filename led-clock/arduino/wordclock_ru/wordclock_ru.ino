// Word Clock RU v2 — ESP32-S3 + WS2812B (256 LEDs, 16×16 grid)
// Natural Russian speech: ЧЕТВЕРТЬ ВОСЬМОГО, БЕЗ ДЕСЯТИ ТРИ
// Time rounded to 5 minutes

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
#define NUM_LEDS    (ROWS * COLS)  // 256
#define BRIGHTNESS  40
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];
const CRGB COLOR_ON  = CRGB(255, 180, 80);
const CRGB COLOR_OFF = CRGB(0, 0, 0);

// Grid 16×16:
//  0: КГДВАДЦАТЬПЯТЬБЖ   ДВАДЦАТЬ ПЯТЬ
//  1: БВКДЕСЯТЬМИНУТГЖ   ДЕСЯТЬ МИНУТ
//  2: ЧЕТВЕРТЬПОЛОВИНА   ЧЕТВЕРТЬ ПОЛОВИНА
//  3: КГБЕЗПЯТИДЕСЯТИД   БЕЗ ПЯТИ ДЕСЯТИ
//  4: ДВАДЦАТИЧЕТВЕРТИ   ДВАДЦАТИ ЧЕТВЕРТИ
//  5: КПЕРВОГОВТОРОГОГ   ПЕРВОГО ВТОРОГО
//  6: ТРЕТЬЕГОДЕСЯТОГО   ТРЕТЬЕГО ДЕСЯТОГО
//  7: ЧЕТВЁРТОГОПЯТОГО   ЧЕТВЁРТОГО ПЯТОГО
//  8: ШЕСТОГОСЕДЬМОГОК   ШЕСТОГО СЕДЬМОГО
//  9: ВОСЬМОГОДЕВЯТОГО   ВОСЬМОГО ДЕВЯТОГО
// 10: КГОДИННАДЦАТОГОД   ОДИННАДЦАТОГО
// 11: КГДВЕНАДЦАТОГОБД   ДВЕНАДЦАТОГО
// 12: ЧАСДВАТРИЧЕТЫРЕК   ЧАС ДВА ТРИ ЧЕТЫРЕ
// 13: ШЕСТЬСЕМЬВОСЕМЬК   ШЕСТЬ СЕМЬ ВОСЕМЬ
// 14: ДЕВЯТЬДВЕНАДЦАТЬ   ДЕВЯТЬ ДВЕНАДЦАТЬ
// 15: КГБОДИННАДЦАТЬДП   ОДИННАДЦАТЬ

struct WordPos { uint8_t row; uint8_t col_start; uint8_t col_end; };

// ── Minute/modifier words (rows 0-4) ──
const WordPos W_DVADTSAT  = {0,  2, 10};  // ДВАДЦАТЬ
const WordPos W_PYAT      = {0, 10, 14};  // ПЯТЬ (shared: minute & hour 5)
const WordPos W_DESYAT    = {1,  3,  9};  // ДЕСЯТЬ (shared: minute & hour 10)
const WordPos W_MINUT     = {1,  9, 14};  // МИНУТ
const WordPos W_CHETVERT  = {2,  0,  8};  // ЧЕТВЕРТЬ
const WordPos W_POLOVINA  = {2,  8, 16};  // ПОЛОВИНА
const WordPos W_BEZ       = {3,  2,  5};  // БЕЗ
const WordPos W_PYATI     = {3,  5,  9};  // ПЯТИ
const WordPos W_DESYATI   = {3,  9, 15};  // ДЕСЯТИ
const WordPos W_DVADTSATI = {4,  0,  8};  // ДВАДЦАТИ
const WordPos W_CHETVERTI = {4,  8, 16};  // ЧЕТВЕРТИ

// ── Genitive hours (for :05-:30 — "X минут СЛЕДУЮЩЕГО") ──
const WordPos HOURS_GEN[] = {
    {0, 0, 0},       // placeholder
    { 5,  1,  8},    //  1: ПЕРВОГО
    { 5,  8, 15},    //  2: ВТОРОГО
    { 6,  0,  8},    //  3: ТРЕТЬЕГО
    { 7,  0, 10},    //  4: ЧЕТВЁРТОГО
    { 7, 10, 16},    //  5: ПЯТОГО
    { 8,  0,  7},    //  6: ШЕСТОГО
    { 8,  7, 15},    //  7: СЕДЬМОГО
    { 9,  0,  8},    //  8: ВОСЬМОГО
    { 9,  8, 16},    //  9: ДЕВЯТОГО
    { 6,  8, 16},    // 10: ДЕСЯТОГО
    {10,  2, 15},    // 11: ОДИННАДЦАТОГО
    {11,  2, 14},    // 12: ДВЕНАДЦАТОГО
};

// ── Nominative hours (for :00 and :35-:55 — "без X ЧАС") ──
const WordPos HOURS_NOM[] = {
    {0, 0, 0},       // placeholder
    {12,  0,  3},    //  1: ЧАС
    {12,  3,  6},    //  2: ДВА
    {12,  6,  9},    //  3: ТРИ
    {12,  9, 15},    //  4: ЧЕТЫРЕ
    { 0, 10, 14},    //  5: ПЯТЬ (shared with W_PYAT)
    {13,  0,  5},    //  6: ШЕСТЬ
    {13,  5,  9},    //  7: СЕМЬ
    {13,  9, 15},    //  8: ВОСЕМЬ
    {14,  0,  6},    //  9: ДЕВЯТЬ
    { 1,  3,  9},    // 10: ДЕСЯТЬ (shared with W_DESYAT)
    {15,  3, 14},    // 11: ОДИННАДЦАТЬ
    {14,  6, 16},    // 12: ДВЕНАДЦАТЬ
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

struct ClockState { uint8_t hour12; uint8_t minute5; };
bool operator!=(const ClockState& a, const ClockState& b) {
    return a.hour12 != b.hour12 || a.minute5 != b.minute5;
}

void showTime(const ClockState& st) {
    fill_solid(leds, NUM_LEDS, COLOR_OFF);

    uint8_t m = st.minute5;
    uint8_t h = st.hour12;
    uint8_t nh = nextHour(h);

    if (m == 0) {
        // :00 — just the hour
        lightWord(HOURS_NOM[h], COLOR_ON);
    } else if (m <= 30) {
        // :05-:30 — "X минут СЛЕДУЮЩЕГО"
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
        // :35-:55 — "без X СЛЕДУЮЩИЙ"
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
    uint8_t m5 = (t.tm_min / 5) * 5;

    ClockState current = {h12, m5};
    if (firstRun || current != lastState) {
        showTime(current);
        lastState = current;
        firstRun = false;
    }
    delay(1000);
}
