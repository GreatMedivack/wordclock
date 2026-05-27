import logging

log = logging.getLogger(__name__)


class EPDDriver:

    def __init__(self):
        self._epd = None
        self._refresh_count = 0
        self._full_refresh_interval = 30

    def init(self):
        from waveshare_epd import epd2in13_V4
        self._epd = epd2in13_V4.EPD()
        self._epd.init()
        self._epd.Clear()
        log.info("e-paper initialized and cleared")

    def show(self, image):
        buf = self._epd.getbuffer(image)

        if self._refresh_count == 0 or self._refresh_count >= self._full_refresh_interval:
            if self._refresh_count > 0:
                self._epd.init()
            self._epd.displayPartBaseImage(buf)
            self._refresh_count = 1
            log.info("full refresh")
        else:
            self._epd.displayPartial(buf)
            self._refresh_count += 1
            log.debug("partial refresh #%d", self._refresh_count)

    def sleep(self):
        if self._epd:
            self._epd.sleep()
            log.info("e-paper entering sleep mode")
