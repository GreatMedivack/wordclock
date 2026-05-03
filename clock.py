import signal
import sys
import time
import logging

import renderer
import time_source

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("clock")

epd = None


def _to_12h(t):
    h24 = t.tm_hour
    ampm = "AM" if h24 < 12 else "PM"
    h12 = h24 % 12
    if h12 == 0:
        h12 = 12
    return h12, ampm


def _shutdown(signum, frame):
    log.info("shutting down (signal %s)", signum)
    if epd:
        epd.sleep()
    sys.exit(0)


def main():
    global epd

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        from epd_driver import EPDDriver
        epd = EPDDriver()
        epd.init()
        has_display = True
    except Exception as e:
        log.warning("e-paper not available, preview-only mode: %s", e)
        has_display = False

    log.info("word clock started")

    while True:
        t = time_source.get_time()
        h12, ampm = _to_12h(t)
        tens = t.tm_min // 10
        ones = t.tm_min % 10

        img = renderer.render(h12, tens, ones, ampm)

        if has_display:
            if epd._refresh_count == 0:
                epd.show_base(img)
            epd.show(img)
        else:
            img.save("preview.png")
            log.info("preview saved: %d:%02d %s", h12, t.tm_min, ampm)

        sleep_sec = 60 - time.localtime().tm_sec
        if sleep_sec <= 0:
            sleep_sec = 60
        time.sleep(sleep_sec)


if __name__ == "__main__":
    main()
