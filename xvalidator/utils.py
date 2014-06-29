import logging
import sys
from itertools import count

__author__ = 'bernd'


class MessageCounter(object):
    _counters = {}

    def __init__(self):
        self.__dict__ = self._counters
        self.reset()
        # self.__dict__['_errors'] = 0
        # self.__dict__['_warnings'] = 0

    def set_errors(self, val):
        self._errors = val

    def get_errors(self):
        return getattr(self, '_errors')

    def set_warnings(self, val):
        self._warnings = val

    def get_warnings(self):
        return getattr(self, '_warnings')

    def reset(self):
        self.errors = 0
        self.warnings = 0

    errors = property(get_errors, set_errors)
    warnings = property(get_warnings, set_warnings)


class CommonEqualityMixin(object):
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

msg_counter = MessageCounter()

error_counter = count()
error_count = next(error_counter)
warning_counter = count()
warning_count = next(warning_counter)

def debug(log, msg):
    if log.isEnabledFor(logging.DEBUG):
        log.debug(msg)


def warning(log, msg):
    global warning_count, warning_counter, msg_counter
    msg_counter.warnings += 1
    warning_count = next(warning_counter)
    log.warning(msg)


def error(log, msg):
    global error_count, error_counter, msg_counter
    msg_counter.errors += 1
    error_count = next(error_counter)
    print('utils: error_count', msg_counter.errors)
    log.error(msg)


# class CallCounted(object):
#     """Decorator to determine number of calls for a method"""
#
#     def __init__(self, method):
#         self.method = method
#         self.counter = 0
#         self.max_value = 100
#
#     def __call__(self, *args, **kwargs):
#         self.counter += 1
#         if self.max_value and self.counter < self.max_value:
#             return self.method(*args, **kwargs)
#
#     def set_max_value(self, max_value):
#         self.max_value = max_value
#
#     def reset(self):
#         self.counter = 0
#
#     @property
#     def value(self):
#         return self.counter
#
#
# error = CallCounted(error)
# warning = CallCounted(warning)


def reset_message_counters(name=''):
    global warning_counter
    global warning_count
    global error_counter
    global error_count
    global msg_counter
    logging.warning('Resetting error count ' + name)
    warning_counter = count()
    error_counter = count()
    msg_counter.reset()
    error_count = next(error_counter)
    warning_count = next(warning_counter)


def message_count_info(log, id_string, abort_on_errors=True):
    global warning_count
    global error_count
    log.info("%s finished with %d error(s) and %d warning(s)." % (id_string, error_count, warning_count))
    if abort_on_errors and error_count:
        print("%s finished with %d error(s)." % (id_string, error_count))
        sys.exit(1)
