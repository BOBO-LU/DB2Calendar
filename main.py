import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from update import sync_process


class MyEventHandler(LoggingEventHandler):
    def on_modified(self, event):
        super(MyEventHandler, self).on_modified(event)
        sync_process()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    observer = Observer()
    observer.schedule(MyEventHandler(), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()