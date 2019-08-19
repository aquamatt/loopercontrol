import importlib
import time


class Intervals(object):
    """
    Measure intervals between press and release

    IN_FRAME means that we are in the period between a press and a release.
    This removes auto-repeat from the calculation, as auto-repeat just
    generates a lot of key press events and no key release events.
    """
    def __init__(self):
        self.last = 0
        self.cache_delta = 0
        self.IN_FRAME = False
        self.start = self._start

    def _get_delta(self):
        now = time.time()
        self.cache_delta = now - self.last
        self.last = now
        return self.cache_delta

    def _start(self):
        if self.IN_FRAME:
            return
        delta = self._get_delta()
        self.IN_FRAME = True
        return delta

    def _ignore_start(self):
        """
        When bound to 'start' this will replace itself with the real
        start when called, thus causing the call to 'start' to be ignored
        just once.
        """
        self.start = self._start
        return self.cache_delta

    def stop(self):
        if not self.IN_FRAME:
            return
        delta = self._get_delta()
        self.IN_FRAME = False
        return delta

    def ignore_next(self):
        """
        Ignore the next start command, but return cached delta
        """
        self.start = self._ignore_start


def get_class_from_string(classpath):
    module_name, klass = classpath.rsplit(".", 1)
    Klass = getattr(importlib.import_module(module_name), klass)
    return Klass
