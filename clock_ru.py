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
    h12 = t.tm_hour % 12
    if h12 == 0:
        h12 = 12
    return h12


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
        h12 = _to_12h(t)
        minute = t.tm_min
        key = (h12, minute)

        if key != last_key:
            img = renderer.render(h12, minute)
            if has_display:
                epd.show(img)
            else:
                img.save("preview.png")
                log.info("preview saved: %d:%02d", h12, minute)
            last_key = key

        time.sleep(5)


if __name__ == "__main__":
    main()
