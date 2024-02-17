"""
Spinner provides a way to run a function in a separate thread and display a
spinner while waiting for the function to complete.  It doesn't spin, but,
rahter, it shows lines across the screen to denote seconds passed.  This
allows the user to visually see how long something took relative to other
things on the screen.
"""

import sys
import time
import threading

class Spinner:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.spinner_thread = None
        self.response = None

    def _spinning_cursor(self) -> str:
        while self.spinner_thread.is_alive():
            for i in range(9):
                yield "≈"
                time.sleep(0.1)
            yield "•"

    def start(self, target_function, *args, **kwargs):
        self.spinner_thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
        self.spinner_thread.start()
        spinner = self._spinning_cursor()
        sys.stdout.write("Waiting for response ")

        for _ in range(self.timeout * 10):
            try:
                sys.stdout.write(next(spinner))
            except StopIteration:
                sys.stdout.write("!")
            sys.stdout.flush()

            if self.response is not None:
                break

    def set_response(self, response):
        self.response = response
