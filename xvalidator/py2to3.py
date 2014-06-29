import sys

__author__ = 'bernd'

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str # pragma: no cover
    integer_types = int # pragma: no cover
    text_type = str # pragma: no cover
    binary_type = bytes # pragma: no cover
    MAXSIZE = sys.maxsize # pragma: no cover
else:
    string_types = basestring # pragma: no cover
    integer_types = (int, long) # pragma: no cover
    text_type = unicode # pragma: no cover
    binary_type = str # pragma: no cover



