import sys
import time
import itertools
import threading


class Spinner:
    def __init__(self, delay=0.1):
        self.spinner_generator = itertools.cycle(['-', '/', '|', '\\'])
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()
        return True

    def stop(self):
        self.busy = False
        time.sleep(self.delay)
        return True
