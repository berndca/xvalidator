from abc import ABCMeta, abstractmethod
from copy import copy
import logging
import random
import re

import six

from xvalidator import utils


__author__ = 'bernd'

logger = logging.getLogger(__name__)


class ValidationException(Exception):
    def __init__(self, msg, value):
        super(ValidationException, self).__init__(self, msg, value)
        self._msg = msg
        self._value = value

    # def __unicode__(self):
    # return '%s, value:%r' %(self._msg, self._value)

    def __str__(self):
        return '%s, value:%r' % (self._msg, self._value)


class Validator:
    __metaclass__ = ABCMeta
    default_build_value = None

    # def __unicode__(self):
    # return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, copy(value))

    @abstractmethod
    def to_python(self, value, **kwargs):
        return value

    @abstractmethod
    def build(self, *args, **kwargs):
        if args:
            value = args[0]
        else:
            if not self.default_build_value is None:
                value = self.default_build_value
            else:
                value = self.__class__.__name__
        return self.to_python(value, **kwargs)


class RangeValidator(Validator):
    min = None
    max = None

    def to_python(self, value, **kwargs):
        if self.min is not None:
            if value < self.min:
                msg = 'Expecting value greater than %d', self.min
                raise ValidationException(msg, value)
        if self.max is not None:
            if value > self.max:
                msg = 'Expecting value less than %d', self.max
                raise ValidationException(msg, value)
        return value

    def build(self, *args, **kwargs):
        return super(RangeValidator, self).build(*args, **kwargs)


class BaseStringValidator(Validator):
    minLength = None
    maxLength = None

    def to_python(self, value, **kwargs):
        if not isinstance(value, six.string_types):
            raise ValidationException('Expecting value of type six.string_types.', value)
        if self.minLength is not None:
            if len(value) < self.minLength:
                msg = 'Expecting value greater than %d', self.minLength
                raise ValidationException(msg, value)
        if self.maxLength is not None:
            if len(value) > self.maxLength:
                msg = 'Expecting value less than %d', self.maxLength
                raise ValidationException(msg, value)
        return value

    def build(self, *args, **kwargs):
        return super(BaseStringValidator, self).build(*args, **kwargs)


class RegexValidator(BaseStringValidator):
    regex = r''

    messages = dict(
        invalid='The input is not valid')

    def to_python(self, value, **kwargs):
        string_value = super(RegexValidator, self).to_python(value)
        regex = re.compile(self.regex)
        if not regex.search(string_value):
            raise ValidationException(self.messages['invalid'], value)
        return string_value


class StringValidator(BaseStringValidator):
    minLength = None
    maxLength = None


class Token(StringValidator):
    """
    Tokens are strings without leading and trailing whitespaces. All other
    whitespaces are collapsed.
    """
    messages = dict(
        badEncoding='Invalid data or incorrect encoding',
        invalid="""Whitespaces should be collapsed in a token."""
    )

    def to_python(self, value, **kwargs):
        string_value = super(Token, self).to_python(value)
        if ' '.join(string_value.split()) != string_value.strip():
            raise ValidationException(self.messages['invalid'], value)
        return string_value


class Name(RegexValidator):
    """
    Values of this type must start with a letter, underscore (_), or colon (:),
    and may contain only letters, digits, underscores (_), colons (:), hyphens
    (-), and periods (.). Colons should only be used to separate namespace
    prefixes from local names.
    """
    default_build_value = 'prefix:Name'
    regex = r'^[a-zA-Z:_][\w:_\-\.]*$'
    messages = dict(
        invalid="""A name needs to begin with a letter, colon (:), or
underscore (_) and shall only contain letters, numbers, and the colon (:),
underscore (_), dash (-), and dot (.) characters. Only one colon (:) total."""
    )
    strip = True
    not_empty = True

    def to_python(self, value, **kwargs):
        if value.count(':') > 1:
            raise ValidationException(self.messages['invalid'], value)
        return super(Name, self).to_python(value)


class NCName(RegexValidator):
    """
    The type NCName represents an XML non-colonized name, which is simply a
    name that does not contain colons. An NCName must start with either a
    letter or underscore (_) and may contain only letters, digits, underscores
    (_), hyphens (-), and periods (.). This is identical to the Name type,
    except that colons are not permitted.
    """
    regex = r'^[a-zA-Z_][\w_\-\.]*$'
    messages = dict(
        invalid="""A name needs to begin with a letter, or underscore (_) and
shall only contain letters, numbers, and the underscore (_), dash (-), and dot
(.) characters."""
    )
    strip = True
    not_empty = True


class Language(RegexValidator):
    """
    The type language represents a natural language identifier, generally used
    to indicate the language of a document or a part of a document. Before
    creating a new attribute of type language, consider using the xml:lang
    attribute that is intended to indicate the natural language of the element
    and its content.  Values of the language type conform to RFC 3066, Tags
    for the Identification of Languages, in version 1.0 and to RFC 4646, Tags
    for Identifying Languages, and RFC 4647, Matching of Language Tags, in
    version 1.1. The three most common formats are:  For ISO-recognized
    languages, the format is a two- or three-letter (usually lowercase)
    language code that conforms to ISO 639, optionally followed by a hyphen
    and a two-letter, usually uppercase, country code that conforms to
    ISO 3166. For example, en or en-US. For languages registered by the
    Internet Assigned Numbers Authority (IANA), the format is i-langname,
    where langname is the registered name. For example, i-navajo.
    For unofficial languages, the format is x-langname, where langname is a
    name of up to eight characters agreed upon by the two parties sharing the
    document. For example, x-Newspeak.  Any of these three formats may have
    additional parts, each preceded by a hyphen, which identify more countries
    or dialects. Schema processors will not verify that values of the language
    type conform to the above rules. They will simply validate them based on
    the pattern specified for this type, which says that it must consist of
    one or more parts of up to eight characters each, separated by hyphens.
    """
    default_build_value = 'en-us'
    regex = r'^([a-zA-Z]{1,8})(-[a-zA-Z]{1,8})*$'
    messages = dict(
        invalid="""A language identifier consists of parts of one to eight
letters separated by a dash (-)."""
    )
    strip = True
    not_empty = True


class NMTOKEN(RegexValidator):
    """
    The type NMTOKEN represents a single string token. NMTOKEN values may
    consist of letters, digits, periods (.), hyphens (-), underscores (_), and
    colons (:). They may start with any of these characters. NMTOKEN has a
    whitespace facet value of collapse, so any leading or trailing whitespace
    will be removed. However, no whitespace may appear within the value itself.
    """
    regex = r'^[\w:_\-\.]+$'
    messages = dict(
        invalid='A nmtoken shall only contain letters, numbers,\
 and the colon (:), underscore (_), dash (-), and dot (.) characters.')
    strip = True
    not_empty = True


class IntegerValidator(RangeValidator):
    default_build_value = 0
    messages = dict(
        integer='Please enter an integer value.')

    def to_python(self, value, **kwargs):
        try:
            result = int(value)
            return super(IntegerValidator, self).to_python(result)
        except ValueError:
            raise ValidationException('Expecting int', value)


class NonNegativeInteger(IntegerValidator):
    default_build_value = 0
    min = 0
    messages = dict(
        integer='Please enter a non negative integer value.')
    not_empty = True


class PositiveInteger(IntegerValidator):
    default_build_value = 1
    min = 1
    messages = dict(
        integer='Please enter a positive integer value.')
    not_empty = True


class NegativeInteger(IntegerValidator):
    default_build_value = -1
    max = -1
    messages = dict(
        integer='Please enter a negative integer value.')
    not_empty = True


class FloatValidator(RangeValidator):
    default_build_value = 3.14
    messages = dict(
        number='Please enter a float Number.')
    not_empty = True

    def to_python(self, value, **kwargs):
        try:
            float_value = float(value)
            super(FloatValidator, self).to_python(float_value)
            return float_value
        except (ValueError, TypeError):
            raise ValidationException(self.messages['number'], value)


class NonNegativeFloat(FloatValidator):
    default_build_value = 0.0
    min = 0
    messages = dict(
        number='Please enter a non negative Number.')
    not_empty = True


class BooleanValidator(BaseStringValidator):
    """
    Converts a string to a boolean.

    """
    true_values = ['true', 't', 'yes', 'y', 'on', '1']
    false_values = ['false', 'f', 'no', 'n', 'off', '0']

    def to_python(self, value, **kwargs):
        if isinstance(value, bool):
            return bool(value)
        string_value = super(BooleanValidator, self).to_python(value)
        if string_value.lower() in self.true_values:
            return True
        if string_value.lower() in self.false_values:
            return False
        raise ValidationException('Could not recognize boolean.', value)

    def build(self, *args, **kwargs):
        self.default_build_value = random.choice(self.true_values+self.false_values)
        return super(BooleanValidator, self).build(*args, **kwargs)


class EnumValidator(BaseStringValidator):
    """
    Tests that the value is one of the members of a given list (options). There
    can be no empty strings in options. value has to be a string.

    If matchLower is True it will also compare value.lower() with the lower case
    version of all strings in options.
    """

    options = ['']
    matchLower = True

    messages = dict(
        invalid='Invalid value',
        notIn='Value must be one of: %(items)s (not %(value)r)')

    def __init__(self, **kwargs):
        super(EnumValidator, self).__init__(**kwargs)
        assert isinstance(self.options, list), 'options need to be a list of strings.'
        all_members_strings = True
        for item in self.options:
            all_members_strings = all_members_strings and isinstance(item, six.string_types)
        assert all_members_strings, 'options need to be a list of strings.'
        self.lookup = None
        self.lookup_lower = None

    def to_python(self, value, **kwargs):
        string_value = super(EnumValidator, self).to_python(value)
        if not self.lookup:
            self.lookup = {item for item in self.options}
        if not self.lookup_lower:
            self.lookup_lower = {item.lower(): item for item in self.options}
        if string_value in self.lookup:
            return string_value
        lower_case_value = string_value.lower()
        if lower_case_value in self.lookup_lower:
            correct_value = self.lookup_lower[lower_case_value]
            utils.warning(logger, 'Found incorrect spelling of option "%s" instead of "%s" in field "%s".'
                          % (string_value, correct_value, self.__class__.__name__))
            return correct_value
        raise ValidationException(self.messages['notIn'] % dict(items=self.items,
                                                                value=value), value)

    def build(self, *args, **kwargs):
        self.default_build_value = random.choice(self.options)
        return super(EnumValidator, self).build(*args, **kwargs)

    @property
    def items(self):
        return '; '.join(map(str, self.options))
