import signal
import sys
import time
import logging

import renderer_ru as renderer
import time_source

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("clock_ru")

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

    log.info("word clock RU started")

    last_key = None
    while True:
        t = time_source.get_time()
        h12, ampm = _to_12h(t)
        tens = t.tm_min // 10
        ones = t.tm_min % 10
        key = (h12, tens, ones, ampm)

        if key != last_key:
            img = renderer.render(h12, tens, ones, ampm)
            if has_display:
                epd.show(img)
            else:
                img.save("preview.png")
                log.info("preview saved: %d:%02d %s", h12, t.tm_min, ampm)
            last_key = key

        time.sleep(5)


if __name__ == "__main__":
    main()
