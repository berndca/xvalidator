import logging

import nose
from nose.tools import raises

from xvalidator import validators, InitKeyStore, KeyName, Stores
from xvalidator.element import Element
from xvalidator.schemas import Choice, ElementSchema, SequenceSchema
from xvalidator.utils import errorCounter, reset_message_counters, warningCounter


__author__ = 'bernd'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

name = ElementSchema('name', minOccurs=1)
wire = ElementSchema('wire', minOccurs=1)
transaction = ElementSchema('transaction', minOccurs=1)
count = ElementSchema('count')
either = ElementSchema('either', minOccurs=1)
orValidator = ElementSchema('or', minOccurs=1)
timing = ElementSchema('timing', minOccurs=1)
drive0 = ElementSchema('drive')
drive1 = ElementSchema('drive', minOccurs=1)
load0 = ElementSchema('load')
load1 = ElementSchema('load', minOccurs=1)


def test_choice_keys_str_single_list_pass():
    choice = Choice(options=[wire, transaction])
    nose.tools.eq_(choice.choice_keys_str(), '(wire | transaction)')


def test_str_unicode_pass():
    choice = Choice(options=[wire, transaction])
    nose.tools.eq_(str(choice), u'Choice: (wire | transaction)')


def test_choice_keys_str_nested_list_2_levels_pass():
    choice = Choice(options=[name, [transaction, drive0], [wire, count]])
    nose.tools.eq_(choice.choice_keys_str(),
                   '(name | (transaction, drive) | (wire, count))')


def test_choice_keys_str_nested_list_2_levels_empty_pass():
    choice = Choice(options=[name, [transaction, drive0], [wire, count], []])
    nose.tools.eq_(choice.choice_keys_str(),
                   '(name | (transaction, drive) | (wire, count) | ())')


def test_match_sequence_choice_pass():
    class Test(SequenceSchema):
        sequence = [name,
                    Choice(options=[wire, transaction]),
                    count
                    ]

    value_keys = ['name', 'wire']
    actual = Test().match_sequence(value_keys)
    nose.tools.eq_(actual, [name, wire])


def test_match_sequence_no_choice_pass():
    class Test(SequenceSchema):
        sequence = [name, wire, count]

    value_keys = ['name', 'wire']
    actual = Test().match_sequence(value_keys)
    nose.tools.eq_(actual, [name, wire])


def test_match_sequence_missing_required_fail():
    class Test(SequenceSchema):
        sequence = [name, count, wire, transaction]

    value_keys = ['name', 'wire']
    reset_message_counters()
    actual = Test().match_sequence(value_keys)
    nose.tools.eq_([len(actual), errorCounter.value], [2, 1])


def test_match_sequence_extra_keys_fail():
    class Test(SequenceSchema):
        sequence = [name, count, wire]

    value_keys = ['name', 'wire', 'extra_key']
    reset_message_counters()
    actual = Test().match_sequence(value_keys)
    nose.tools.eq_([len(actual), errorCounter.value], [2, 1])


def test_match_sequence_basic_two_last_fail():
    class Test(SequenceSchema):
        sequence = [name,
                    Choice(options=[wire, transaction]),
                    count
                    ]

    value_keys = ['name', 'wire', 'transaction']
    reset_message_counters()
    actual = Test().match_sequence(value_keys)
    nose.tools.eq_([len(actual), errorCounter.value], [3, 1])


def test_match_sequence_unused_choice_pass():
    class Test(SequenceSchema):
        sequence = [name,
                    Choice(options=[drive0, load0]),
                    count
                    ]

    value_keys = ['name', 'count']
    reset_message_counters()
    Test().match_sequence(value_keys)
    nose.tools.eq_(errorCounter.value, 0)


def test_choice_to_key_sets_multiple_required_true_pass():
    choice = Choice(options=[
        ElementSchema('addressBlock', minOccurs=1),
        ElementSchema('bank', minOccurs=1),
        ElementSchema('subspaceMap', minOccurs=1),
    ])
    min_key_sets = choice.choice_to_key_sets(required=True)
    expected = [{'addressBlock'}, {'bank'}, {'subspaceMap'}]
    nose.tools.eq_(min_key_sets, expected)


def test_choice_to_key_sets_multiple_required_false_pass():
    choice = Choice(options=[
        ElementSchema('addressBlock', minOccurs=1),
        ElementSchema('bank', minOccurs=1),
        [
            ElementSchema('test', minOccurs=1),
            ElementSchema('optional'),
        ],
        ElementSchema('subspaceMap', minOccurs=1),
    ])
    max_key_sets = choice.choice_to_key_sets(required=False)
    expected = [set([]), set([]), {'optional'}, set([])]
    nose.tools.eq_(max_key_sets, expected)


def test_choice_basic_two_pass():
    choice = Choice(options=[either, orValidator])
    value_key_set = {'or'}
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [orValidator])


def test_choice_basic_two_both_fail():
    choice = Choice(options=[either, orValidator])
    value_key_set = {'either', 'or'}
    reset_message_counters()
    choice.match_choice_keys(value_key_set)
    nose.tools.eq_(errorCounter.value, 1)


def test_choice_basic_two_extra_fail():
    choice = Choice(options=[
        ElementSchema('either', minOccurs=1),
        ElementSchema('or', minOccurs=1),
    ])
    value_key_set = {'extra', 'or'}
    reset_message_counters()
    choice.match_choice_keys(value_key_set)
    nose.tools.eq_(errorCounter.value, 1)


def test_choice_three_options_single_pass():
    choice = Choice(options=[
        [timing, drive0, load0],
        [drive1, load0],
        load1
    ])
    value_key_set = {'timing'}
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [timing])


def test_choice_three_options_two_pass():
    choice = Choice(options=[
        [timing, drive0, load0],
        [drive1, load0],
        load1
    ])
    value_key_set = {'timing', 'load'}
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [timing, load0])


def test_choice_missing_required_fail():
    choice = Choice(options=[name, [drive0, timing]])
    value_key_set = {'drive'}
    reset_message_counters()
    choice.match_choice_keys(value_key_set)
    nose.tools.eq_(errorCounter.value, 1)


def test_choice_missing_required_first_optional_second_fail():
    choice = Choice(options=[[name, load0], [drive0, load0]])
    value_key_set = {'name', 'drive', 'load'}
    reset_message_counters()
    choice.match_choice_keys(value_key_set)
    nose.tools.eq_(errorCounter.value, 1)


useEnumeratedValues = ElementSchema('useEnumeratedValues', minOccurs=1)
minimum = ElementSchema('minimum', minOccurs=1)
maximum = ElementSchema('maximum', minOccurs=1)


def test_choice_three_options_mixed2_pass():
    choice = Choice(options=[
        ElementSchema('writeAsRead', minOccurs=1),
        ElementSchema('useEnumeratedValues', minOccurs=1),
        [
            minimum,
            maximum,
        ]
    ])
    value_key_set = {'minimum', 'maximum'}
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [minimum, maximum])


def test_choice_three_options_mixed_single_pass():
    choice = Choice(options=[
        ElementSchema('writeAsRead', minOccurs=1),
        useEnumeratedValues,
        [
            minimum,
            maximum,
        ]
    ])
    value_key_set = {'useEnumeratedValues'}
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [useEnumeratedValues])


def test_choice_three_options_one_empty_pass():
    choice = Choice(options=[
        ElementSchema('writeAsRead', minOccurs=1),
        ElementSchema('useEnumeratedValues', minOccurs=1),
        [
            ElementSchema('minimum', minOccurs=1),
            ElementSchema('maximum', minOccurs=1),
        ]
    ], required=False)
    value_key_set = set()
    actual = choice.match_choice_keys(value_key_set)
    nose.tools.eq_(actual, [])


def test_check_key_order_pass():
    reset_message_counters()
    value_keys = ['one', 'two', 'three']

    class Test(SequenceSchema):
        pass

    sequence = [
        ElementSchema('one'),
        ElementSchema('two'),
        ElementSchema('three'),
    ]
    Test().check_key_order(value_keys, sequence)
    nose.tools.eq_([warningCounter.value, errorCounter.value], [0, 0])


def test_check_key_order_warning_pass():
    reset_message_counters()
    value_keys = ['two', 'one', 'three']

    class Test(SequenceSchema):
        pass

    sequence = [
        ElementSchema('one'),
        ElementSchema('two'),
        ElementSchema('three'),
    ]
    Test().check_key_order(value_keys, sequence)
    nose.tools.eq_(warningCounter.value, 1)


def test_validate_attributes():
    schema = ElementSchema('test', attributes=[
        ElementSchema('usageType', validator=validators.Name()),
        ElementSchema('exampleInt', validator=validators.PositiveInteger()),
        ElementSchema('*'),
    ])
    el_with_attributes = Element('test', value=None,
                                 attributes=dict(
                                 exampleInt='42',
                                 usageType='typed',
                                 otherAttr='other'
                                 ))
    validated = schema.to_python(el_with_attributes)
    nose.tools.eq_(validated.attributes['exampleInt'], 42)


@raises(validators.ValidationException)
def test_to_python_value_no_list_fail():
    class Test(SequenceSchema):
        sequence = [name, count, wire]

    Test().to_python('invalid')


@raises(validators.ValidationException)
def test_to_python_value_no_list_of_element_fail():
    class Test(SequenceSchema):
        sequence = [name, count, wire]

    Test().to_python([1, 2, 'name', True])


def test_to_python_pass():
    class Test(SequenceSchema):
        sequence = [name, count, wire]

    element_list = [
        Element('name', value='myName'),
        Element('wire', value='wire0'),
        Element('wire', value='wire1'),
        Element('wire', value='wire2'),
    ]
    expected = [
        Element('name', value='myName'),
        Element('wire', value='wire0'),
        Element('wire', value='wire1'),
        Element('wire', value='wire2'),
    ]
    for element in expected:
        element.isValidated = True
        test_instance = Test()
    actual = test_instance.to_python(element_list)
    nose.tools.eq_(actual, expected)


def test_sequence_schema_initial_pass():
    class RegisterField(SequenceSchema):
        sequence = [ElementSchema('spirit:name',
            validator=KeyName(key_names='fieldKey', level=2))]


    class Register(SequenceSchema):
        initial = InitKeyStore('fieldKey')
        sequence = [ElementSchema('spirit:field', validator=RegisterField())]


    reset_message_counters()
    register_path = '/register-0,'
    field0_path = register_path + '/field-0,field0'
    field1_path = register_path + '/field-1,field1'
    field0_name_path = field0_path + '/name-0,field0'
    field1_name_path = field1_path + '/name-1,field1'
    field0 = Element('spirit:field', path=field0_path,
        value=[Element('spirit:name', path=field0_name_path, value='field0')])
    field1 = Element('spirit:field', path=field1_path,
        value=[Element('spirit:name', path=field1_name_path, value='field1')])
    register = Element('register', path=register_path, value=[field0, field1])
    stores = Stores()
    Register().to_python(register.value, path=register.path,
        stores=stores)
    nose.tools.eq_(errorCounter.value, 0)
