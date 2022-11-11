#!/usr/bin/env python3

import logging
from signal import sigwait, SIGINT

from threading import Thread, Event
from zeroconf import Zeroconf, ServiceInfo


def enable_debug():
    logging.basicConfig(
        format="[%(levelname)s %(asctime)s]: %(message)s", level=logging.DEBUG
    )


APPTYPE = "_crosine-raven._tcp.local."


def generate_name(name: str) -> str:
    return f"{name}.{APPTYPE}"


class ZeroConfThread(Thread):
    _log = logging.getLogger("ZCT")

    zconf: Zeroconf
    sinfo: ServiceInfo
    sevent: Event

    def __init__(self):
        Thread.__init__(self)
        self.zconf = Zeroconf()
        self.sinfo = ServiceInfo(
            APPTYPE,
            generate_name("helloserv"),
            8081,
            0,
            0,
            b"",
            f"_crs-raven._tcp.local.",
        )
        self.sevent = Event()

    def run(self):
        self._log.info("REGISTERING")
        self.zconf.register_service(self.sinfo)
        self._log.info("REGISTERED")
        self.sevent.wait()
        self._log.info("UNREGISTER")
        self.zconf.unregister_service(self.sinfo)
        self.zconf.close()


def main():
    enable_debug()
    zct = ZeroConfThread()
    zct.start()
    sigwait([SIGINT])
    zct.sevent.set()
    zct.join()


if __name__ == "__main__":
    main()
