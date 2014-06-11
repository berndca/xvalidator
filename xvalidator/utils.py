import logging
import sys

__author__ = 'bernd'


class CommonEqualityMixin(object):
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


def debug(log, msg):
    if log.isEnabledFor(logging.DEBUG):
        log.debug(msg)


def warning(log, msg):
    log.warning(msg)


def error(log, msg):
    log.error(msg)


class CallCounted(object):
    """Decorator to determine number of calls for a method"""

    def __init__(self, method):
        self.method = method
        self.counter = 0
        self.max_value = 100

    def __call__(self, *args, **kwargs):
        self.counter += 1
        if self.max_value and self.counter < self.max_value:
            return self.method(*args, **kwargs)

    def set_max_value(self, max_value):
        self.max_value = max_value

    def reset(self):
        self.counter = 0

    @property
    def value(self):
        return self.counter


errorCounter = CallCounted(error)
warningCounter = CallCounted(warning)

error = errorCounter
warning = warningCounter


def reset_message_counters():
    errorCounter.reset()
    warningCounter.reset()


def message_count_info(log, id_string, abort_on_errors=True):
    log.info("%s finished with %d error(s) and %d warning(s)." % (id_string, errorCounter.value, warningCounter.value))
    if abort_on_errors and errorCounter.value:
        print("%s finished with %d error(s)." % (id_string, errorCounter.value))
        sys.exit(1)
