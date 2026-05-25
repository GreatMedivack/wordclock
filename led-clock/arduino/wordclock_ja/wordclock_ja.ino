// Word Clock JA — ESP32-S3 + WS2812B (80 LEDs, 8×10 kanji grid)
// Displays: 午後 五時 四七分 (5:47 PM)

#include <FastLED.h>
#include <WiFi.h>
#include <time.h>

const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* NTP_SERVER    = "pool.ntp.org";
const long  GMT_OFFSET    = 9 * 3600;  // JST (UTC+9)
const int   DST_OFFSET    = 0;

#define LED_PIN    48
#define COLS       10
#define ROWS       8
#define NUM_LEDS   (ROWS * COLS)  // 80
#define BRIGHTNESS 40
#define LED_TYPE   WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];
const CRGB COLOR_ON  = CRGB(255, 180, 80);
const CRGB COLOR_OFF = CRGB(0, 0, 0);

// Grid (for reference):
// 0: 午前花午後雲時計夢光
// 1: 一雪二風三山四森五泉    Hours 1-5
// 2: 六波七虹八鳥九竹時霧    Hours 6-9, 時
// 3: 十露十一霜十二月雪空    Hours 10,11,12
// 4: 〇火一水二木三金四土    Tens 0-4
// 5: 五雨〇石一霧二夢三露    Tens 5, Ones 0-3
// 6: 四竹五花六雪七音八鳥    Ones 4-8
// 7: 九海川山森泉波虹風分    Ones 9, 分

struct WordPos { uint8_t row; uint8_t col_start; uint8_t col_end; };

const WordPos AMPM_WORDS[] = {
    {0, 0, 2},   // 0: 午前 (AM)
    {0, 3, 5},   // 1: 午後 (PM)
};

const WordPos HOURS[] = {
    {0, 0, 0},   // placeholder
    {1, 0, 1},   // 1: 一
    {1, 2, 3},   // 2: 二
    {1, 4, 5},   // 3: 三
    {1, 6, 7},   // 4: 四
    {1, 8, 9},   // 5: 五
    {2, 0, 1},   // 6: 六
    {2, 2, 3},   // 7: 七
    {2, 4, 5},   // 8: 八
    {2, 6, 7},   // 9: 九
    {3, 0, 1},   // 10: 十
    {3, 2, 4},   // 11: 十一
    {3, 5, 7},   // 12: 十二
};

const WordPos HOUR_SUFFIX = {2, 8, 9};  // 時

const WordPos TENS_WORDS[] = {
    {4, 0, 1},   // 0: 〇
    {4, 2, 3},   // 1: 一
    {4, 4, 5},   // 2: 二
    {4, 6, 7},   // 3: 三
    {4, 8, 9},   // 4: 四
    {5, 0, 1},   // 5: 五
};

const WordPos ONES_WORDS[] = {
    {5, 2, 3},   // 0: 〇
    {5, 4, 5},   // 1: 一
    {5, 6, 7},   // 2: 二
    {5, 8, 9},   // 3: 三
    {6, 0, 1},   // 4: 四
    {6, 2, 3},   // 5: 五
    {6, 4, 5},   // 6: 六
    {6, 6, 7},   // 7: 七
    {6, 8, 9},   // 8: 八
    {7, 0, 1},   // 9: 九
};

const WordPos MINUTE_SUFFIX = {7, 9, 10};  // 分

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
    lightWord(AMPM_WORDS[st.is_pm], COLOR_ON);
    lightWord(HOURS[st.hour12], COLOR_ON);
    lightWord(HOUR_SUFFIX, COLOR_ON);
    lightWord(TENS_WORDS[st.tens], COLOR_ON);
    lightWord(ONES_WORDS[st.ones], COLOR_ON);
    lightWord(MINUTE_SUFFIX, COLOR_ON);
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
        delay(20);
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
    Serial.println("Word Clock JA ready");
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
