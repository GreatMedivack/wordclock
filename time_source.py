import time
import logging

log = logging.getLogger(__name__)

_rtc = None


def _init_rtc():
    global _rtc
    try:
        import board
        import adafruit_pcf8523
        i2c = board.I2C()
        _rtc = adafruit_pcf8523.PCF8523(i2c)
        log.info("PCF8523 RTC detected on I2C")
    except Exception as e:
        _rtc = None
        log.warning("RTC not available, using system time: %s", e)


def get_time():
    if _rtc is None:
        _init_rtc()

    if _rtc is not None:
        try:
            return _rtc.datetime
        except Exception as e:
            log.warning("RTC read failed, falling back to system time: %s", e)

    return time.localtime()
