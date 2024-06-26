﻿import logging
import sys
import time

from loguru import logger
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

from update import sync_process


class MyEventHandler(LoggingEventHandler):
    def on_modified(self, event):
        # super(MyEventHandler, self).on_modified(event)
        logger.info("detect file change")
        sync_process()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    path = sys.argv[1] if len(sys.argv) > 1 else r"D:\行事曆同步\schk_pin.dbf"

    while True:
        sync_process()
        logging.info("start sleeping")
        time.sleep(60)
        
    # observer = Observer()
    # observer.schedule(MyEventHandler(), path, recursive=True)
    # observer.start()
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()
