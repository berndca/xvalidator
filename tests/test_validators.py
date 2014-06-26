import random
import nose
from nose.tools import raises

from xvalidator.validators import Token, Name, NCName, Language, \
    NMTOKEN, IntegerValidator, NonNegativeInteger, PositiveInteger, \
    NegativeInteger, FloatValidator, NonNegativeFloat, BooleanValidator, \
    EnumValidator, ValidationException, Validator


__author__ = 'bernd'


def test_validation_exception__str__pass():
    iv = ValidationException('message', 42)
    nose.tools.eq_(str(iv), 'message, value:42')


def test_token_Build_value_pass():
    value = ' Test string with collapsed whitespace.'
    actual = Token().build(value)
    nose.tools.eq_(actual, value)


def test_token_build_pass():
    actual = Token().build()
    nose.tools.eq_(actual, 'Token')


def test_token_pass():
    tk = Token()
    value = ' Test string with collapsed whitespace.'
    actual = tk.to_python(value)
    nose.tools.eq_(actual, value)


@raises(ValidationException)
def test_token_whitespace_fail():
    tk = Token()
    value = 'Test string with  uncollapsed whitespace.'
    tk.to_python(value)


@raises(ValidationException)
def test_token_value_type_fail():
    tk = Token()
    value = 21
    tk.to_python(value)


@raises(ValidationException)
def test_token_min_length_fail():
    tk = Token(minLength=8)
    value = 'short'
    tk.to_python(value)


@raises(ValidationException)
def test_token_max_length_fail():
    tk = Token(maxLength=8)
    value = ' value is too long'
    tk.to_python(value)


def test_name_pass():
    validator_inst = Name()
    value = 'ns:Test-Name_0'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, value)


def test_build_name_pass():
    actual = Name().build()
    nose.tools.eq_(actual, 'prefix:Name')


@raises(ValidationException)
def test_name_two_colons_fail():
    validator_inst = Name()
    value = 'ns:Test-Name:0'
    validator_inst.to_python(value)


@raises(ValidationException)
def test_name_whitespace_fail():
    validator_inst = Name()
    value = 'ns:Test-Name 0'
    validator_inst.to_python(value)


def test_ncname_pass():
    validator_inst = NCName()
    value = 'Test-NCName_0'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, value)


def test_build_ncname_pass():
    actual = NCName().build()
    nose.tools.eq_(actual, 'NCName')


@raises(ValidationException)
def test_ncname_whitespace_fail():
    validator_inst = NCName()
    value = 'ns:Test-NCName 0'
    validator_inst.to_python(value)


def test_language_pass():
    validator_inst = Language()
    value = 'En-US'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, value)


def test_build_language_value_pass():
    value = 'En-US'
    actual = Language().build(value)
    nose.tools.eq_(actual, value)


def test_build_language_pass():
    actual = Language().build()
    nose.tools.eq_(actual, 'en-us')


@raises(ValidationException)
def test_language_whitespace_fail():
    validator_inst = Language()
    value = 'En-US lang'
    validator_inst.to_python(value)


@raises(ValidationException)
def test_language_part_too_long_fail():
    validator_inst = Language()
    value = 'En-US-partIsTooLong'
    validator_inst.to_python(value)


def test_nmtoken_pass():
    validator_inst = NMTOKEN()
    value = '.:-_Test-NMTOKEN_0'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, value)


def test_nmtoken_build_pass():
    actual = NMTOKEN().build()
    nose.tools.eq_(actual, 'NMTOKEN')


def test_nmtoken_build_value_pass():
    value = '.:-_Test-NMTOKEN_0'
    actual = NMTOKEN().build(value)
    nose.tools.eq_(actual, value)


@raises(ValidationException)
def test_nmtoken_whitespace_fail():
    value = 'Test-NMTOKEN 0'
    NMTOKEN().to_python(value)


def test_integer_pass():
    validator_inst = IntegerValidator()
    value = '00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, 33)


def test_build_integer_33_pass():
    value = '00033'
    actual = IntegerValidator().build(value)
    nose.tools.eq_(actual, 33)


def test_build_integer_pass():
    actual = IntegerValidator().build()
    nose.tools.eq_(actual, 0)


@raises(ValidationException)
def test_integer_range_fail():
    value = '00abc'
    IntegerValidator().to_python(value)


def test_non_negative_integer_pass():
    validator_inst = NonNegativeInteger()
    value = '00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, 33)


def test_non_negative_integer_build_pass():
    actual = NonNegativeInteger().build()
    nose.tools.eq_(actual, 0)


def test_non_negative_integer_build_value_pass():
    value = '00033'
    actual = NonNegativeInteger().build(value)
    nose.tools.eq_(actual, 33)


@raises(ValidationException)
def test_non_negative_integer_range_fail():
    value = '-33'
    NonNegativeInteger().to_python(value)


def test_positive_integer_pass():
    validator_inst = PositiveInteger()
    value = '00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, 33)


def test_positive_integer_build_pass():
    actual = PositiveInteger().build()
    nose.tools.eq_(actual, 1)


def test_positive_integer_build_value_pass():
    value = '00033'
    actual = PositiveInteger().build(value)
    nose.tools.eq_(actual, 33)


@raises(ValidationException)
def test_positive_integer_range_fail():
    value = '0'
    PositiveInteger().to_python(value)


def test_negative_integer_pass():
    validator_inst = NegativeInteger()
    value = '-00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, -33)


def test_negative_integer_build_pass():
    actual = NegativeInteger().build()
    nose.tools.eq_(actual, -1)


def test_negative_integer_build_value_pass():
    value = '-00033'
    actual = NegativeInteger().build(value)
    nose.tools.eq_(actual, -33)


@raises(ValidationException)
def test_negative_integer_range_fail():
    value = '0'
    NegativeInteger().to_python(value)


def test_float_pass():
    validator_inst = FloatValidator()
    value = '00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, 33)


def test_float_build_pass():
    actual = FloatValidator().build(0)
    nose.tools.eq_(actual, 0.0)


def test_float_build_value_pass():
    value = '00033'
    actual = FloatValidator().build(value)
    nose.tools.eq_(actual, 33)


@raises(ValidationException)
def test_float_range_fail():
    value = '00abc'
    FloatValidator().to_python(value)


def test_non_negative_float_pass():
    validator_inst = NonNegativeFloat()
    value = '00033'
    actual = validator_inst.to_python(value)
    nose.tools.eq_(actual, 33)


def test_non_negative_float_build_pass():
    actual = NonNegativeFloat().build()
    nose.tools.eq_(actual, 0.0)


def test_non_negative_float_build_value_pass():
    value = '00033'
    actual = NonNegativeFloat().build(value)
    nose.tools.eq_(actual, 33)


@raises(ValidationException)
def test_non_negative_float_range_fail():
    validator_inst = NonNegativeFloat()
    value = '-33'
    validator_inst.to_python(value)


def test_boolean_validator_true_pass():
    validator_inst = BooleanValidator()
    actual = validator_inst.to_python('true')
    nose.tools.eq_(actual, True)


def test_boolean_validator_false_pass():
    validator_inst = BooleanValidator()
    actual = validator_inst.to_python('false')
    nose.tools.eq_(actual, False)


def test_build_boolean_validator_pass():
    random.seed(1)
    actual = BooleanValidator().build()
    nose.tools.eq_(actual, True)


def test_build_boolean_validator_value_pass():
    actual = BooleanValidator().build('true')
    nose.tools.eq_(actual, True)


def test_build_boolean_validator_false_pass():
    actual = BooleanValidator().build('false')
    nose.tools.eq_(actual, False)


def test_boolean_validator_bool_true_pass():
    validator_inst = BooleanValidator()
    actual = validator_inst.to_python(True)
    nose.tools.eq_(actual, True)


def test_boolean_validator_bool_false_pass():
    validator_inst = BooleanValidator()
    actual = validator_inst.to_python(False)
    nose.tools.eq_(actual, False)


@raises(ValidationException)
def test_boolean_validator_wrong_type_fail():
    value = '-33'
    BooleanValidator().to_python(value)


@raises(ValidationException)
def test_boolean_validator_wrong_value_fail():
    value = 'not boolean'
    BooleanValidator().to_python(value)


class DriverType(EnumValidator):
    options = [
        "clock",
        "singleShot",
        "any",
    ]


def test_driver_type_pass():
    validator_inst = DriverType()
    actual = validator_inst.to_python('singleShot')
    nose.tools.eq_(actual, 'singleShot')


def test_build_driver_type_pass():
    random.seed(42)
    actual = DriverType().build()
    nose.tools.eq_(actual, 'singleShot')


def test_build_driver_type_value_pass():
    actual = DriverType().build('any')
    nose.tools.eq_(actual, 'any')


def test_driver_type_case_warning_pass():
    validator_inst = DriverType()
    actual = validator_inst.to_python('CLOCK')
    nose.tools.eq_(actual, 'clock')


@raises(ValidationException)
def test_driver_type_value_fail():
    DriverType().to_python('myCLOCK')


@raises(ValidationException)
def test_driver_type_value_type_fail():
    DriverType().to_python(22)


@raises(ValidationException)
def test_driver_type_value_unicode_error_fail():
    DriverType().to_python(u'\x81myCLOCK')


def test_enum_init_pass():
    validator_inst = EnumValidator(options=[
        "clock",
        "singleShot",
        "any",
        ])
    actual = validator_inst.to_python('singleShot')
    nose.tools.eq_(actual, 'singleShot')

