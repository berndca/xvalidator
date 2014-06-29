from __future__ import unicode_literals

from collections import OrderedDict
import nose
from nose.tools import raises

from xvalidator.constraints import Stores, ID
from xvalidator.element import Element
from xvalidator import utils
from xvalidator.schemas import ElementSchema, SequenceSchema
from xvalidator.validators import PositiveInteger, NCName


__author__ = 'bernd'


def test_element_schema_str_pass():
    es = ElementSchema('field')
    nose.tools.eq_(str(es), 'ElementSchema: field')


def test_element_schema_args_min_pass():
    es = ElementSchema('field')
    actual = [es.validator, es.minOccurs, es.unbounded, es.default]
    nose.tools.eq_(actual, [None, 0, False, None])


def test_element_schema_arg_min_unbounded_default_pass():
    es = ElementSchema('field', minOccurs=1, unbounded=True, default='test')
    actual = [es.validator, es.minOccurs, es.unbounded, es.default]
    nose.tools.eq_(actual, [None, 1, True, 'test'])


def test_element_schema_args_attribute_pass():
    attr = ElementSchema('testConstraint')
    es = ElementSchema('testable', attributes=attr)
    actual = [es.validator, es.minOccurs, es.unbounded, es.attributes]
    nose.tools.eq_(actual, [None, 0, False, [attr]])


@raises(AssertionError)
def test_element_schema_extra_args_fail():
    ElementSchema('testable', extra=True)


def test_element_schema_args_attributes_pass():
    attr = [
        ElementSchema('id'),
        ElementSchema('testConstraint'),
    ]
    es = ElementSchema('testable', attributes=attr)
    actual = [es.validator, es.minOccurs, es.unbounded, es.attributes]
    nose.tools.eq_(actual, [None, 0, False, attr])


@raises(AssertionError)
def test_element_schema_args_attributes_wrong_type_fail():
    attr = [
        ElementSchema('id'),
        'testConstraint',
    ]
    ElementSchema('testable', attributes=attr)


def test_element_schema_args_validator_pass():
    class TestValidator(SequenceSchema):
        pass

    test_validator_instance = TestValidator()
    es = ElementSchema('testable', validator=test_validator_instance)
    actual = [es.validator.__class__, es.minOccurs, es.unbounded, es.attributes]
    nose.tools.eq_(actual, [test_validator_instance.__class__, 0, False, []])


def test_element_schema_validate_pass():
    es = ElementSchema('testable', validator=PositiveInteger())
    # noinspection PyProtectedMember
    value = es._validate(es.validator, '42', es._tag, path='/')
    nose.tools.eq_(value, 42)


def test_element_schema_tp_python_validator_None_pass():
    es = ElementSchema('test', validator=None)
    el = Element('test', value=[1, 2], path='/')
    value = es.to_python(el)
    nose.tools.eq_(value, el)


def test_element_schema_tp_python_element_None_pass():
    es = ElementSchema('test', validator=NCName(), minOccurs=0)
    el = Element('test', value=None, path='/')
    value = es.to_python(el)
    nose.tools.eq_(value, el)


def test_element_schema_validate_fail():
    utils.reset_message_counters()
    es = ElementSchema('testable', validator=PositiveInteger())
    # noinspection PyProtectedMember
    es._validate(es.validator, 'NaN', es.tag, path='/')
    nose.tools.eq_(utils.error_count, 1)


def test_element_schema_validate_attributes_min_pass():
    es = ElementSchema('testable', attributes=ElementSchema('index',
                                                            validator=PositiveInteger()))
    element = Element('testable', attributes=dict(index='42'))
    # noinspection PyProtectedMember
    validated_attributes = es._validate_attributes(element)
    nose.tools.eq_(validated_attributes, dict(index=42))


def test_element_schema_validate_attributes_extra_pass():
    es = ElementSchema('testable', attributes=[
        ElementSchema('index', validator=PositiveInteger()), ElementSchema('*')
    ])
    element = Element('testable', attributes=dict(index='42', refer='extra'))
    # noinspection PyProtectedMember
    validated_attributes = es._validate_attributes(element)
    expected_attributes = dict(index=42, refer='extra')
    nose.tools.eq_(validated_attributes, expected_attributes)


def test_element_schema_validate_attributes_extra_fail():
    utils.reset_message_counters()
    es = ElementSchema('testable',
                       attributes=ElementSchema(
                           'index', validator=PositiveInteger()))
    element = Element('testable', attributes=dict(index='42', refer='extra'))
    # noinspection PyProtectedMember
    es._validate_attributes(element)
    nose.tools.eq_(utils.error_count, 1)


def test_element_schema_validate_attributes_validator_none_pass():
    es = ElementSchema('testable', attributes=ElementSchema(
        'index', validator=None))
    element = Element('testable', attributes=dict(index='42'))
    # noinspection PyProtectedMember
    validated_attributes = es._validate_attributes(element)
    nose.tools.eq_(validated_attributes, dict(index='42'))


@raises(AssertionError)
def test_element_schema_to_python_no_element_fail():
    es = ElementSchema('testable', validator=PositiveInteger())
    es.to_python('42')


def test_element_schema_to_python_constraints_id_attribute_pass():
    stores = Stores()
    es = ElementSchema('test', validator=None, attributes=ElementSchema(
        'id', validator=ID()))
    element = Element('test', value='keyValue', path='/test-0,',
                      attributes={'id': 'ID42'})
    es.to_python(element, path=element.path, stores=stores)
    nose.tools.eq_(stores.idStore.keys, {'ID:/': {'ID42': '/test-0,@id'}})


def test_element_schema_to_python_int_list_pass():
    es = ElementSchema('numbers', validator=PositiveInteger())
    element = Element('numbers', value=['1', 2, 3, '4'], path='/top-0,name')
    expected = Element('numbers', value=[1, 2, 3, 4], path='/top-0,name')
    expected.isValidated = True
    actual = es.to_python(element)
    nose.tools.eq_(actual, expected)


def test_element_schema_to_python_sequence_schema_pass():
    class TestSchema(SequenceSchema):
        sequence = [ElementSchema('name', validator=NCName()),
                    ElementSchema('count', validator=PositiveInteger())]

    es = ElementSchema('test', validator=TestSchema())
    path = '/test-0,testName'
    name = Element('name', value='testName', path=path + '/name-0,')
    count = Element('count', value='3', path=path + '/count-0,')
    element = Element('test', value=[name, count], path=path)
    validated_name = Element(tag='name', path="/test-0,testName/name-0,",
                             value='testName')
    validated_name.isValidated = True
    validated_count = Element(tag='count', path="/test-0,testName/count-0,",
                              value=3)
    validated_count.isValidated = True
    expected = Element(tag='test', path="/test-0,testName", value=[
        validated_name,
        validated_count])
    for el in expected.value:
        el.isValidated = True
    expected.isValidated = True
    actual = es.to_python(element)
    nose.tools.eq_(actual, expected)


def test_element_schema_build_no_value_no_attributes_pass():
    es = ElementSchema('name', validator=NCName())
    path='/name-0,NCName,'
    actual = es.build(path=path)
    expected = Element('name', value='NCName', path=path)
    nose.tools.eq_(actual, expected)


def test_element_schema_build_no_value_with_attributes_pass():
    es = ElementSchema('name', validator=NCName(), attributes=[
        ElementSchema('id', validator=ID()),
        ElementSchema('offset', validator=PositiveInteger()),
    ])
    path='/name-0,NCName,'
    stores = Stores()
    actual = es.build(path=path, stores=stores)
    expected = Element('name', value='NCName', path=path, attributes=
    OrderedDict([('id', 'testId0'), ('offset', 1)]))
    expected.isValidated = True
    validated = es.to_python(actual, path=path, stores=Stores())
    nose.tools.eq_(validated, expected)


def test_element_schema_build_no_value_with_attributes_validator_none_pass():
    es = ElementSchema('parent', validator=None, attributes=[
        ElementSchema('id', validator=ID()),
        ElementSchema('offset', validator=PositiveInteger()),
    ])
    path='/name-0,NCName,'
    stores = Stores()
    actual = es.build(path=path, stores=stores)
    expected = Element('parent', value=None, path=path, attributes=
    OrderedDict([('id', 'testId0'), ('offset', 1)]))
    expected.isValidated = True
    validated = es.to_python(actual, path=path, stores=Stores())
    nose.tools.eq_(validated, expected)


def test_element_schema_build_no_value_with_star_attribute_pass():
    es = ElementSchema('name', validator=NCName(), attributes=[
        ElementSchema('id', validator=ID()),
        ElementSchema('*', validator=None),
        ElementSchema('offset', validator=PositiveInteger()),
    ])
    path='/name-0,NCName,'
    stores = Stores()
    actual = es.build(path=path, stores=stores)
    expected = Element('name', value='NCName', path=path, attributes=
    OrderedDict([('id', 'testId0'), ('offset', 1)]))
    nose.tools.eq_(actual, expected)


def test_element_schema_build_no_value_unbounded_int_pass():
    es = ElementSchema('dim', validator=PositiveInteger(), unbounded=True)
    path='/dim-0,'
    stores = Stores()
    actual = es.build(path=path, stores=stores)
    expected = Element('dim', value=[1, 1, 1, 1, 1], path=path)
    nose.tools.eq_(actual, expected)


def test_element_schema_build_no_value_unbounded_maxoccurs_pass():
    es = ElementSchema('dim', validator=PositiveInteger(), unbounded=True)
    path='/dim-0,'
    stores = Stores()
    actual = es.build(path=path, stores=stores, maxOccurs=2)
    expected = Element('dim', value=[1, 1], path=path)
    nose.tools.eq_(actual, expected)


def test_element_schema_build_no_value_unbounded_minoccurs2_pass():
    es = ElementSchema('dim', validator=PositiveInteger(), unbounded=True,
    minOccurs=2)
    path='/dim-0,'
    stores = Stores()
    actual = es.build(path=path, stores=stores)
    expected = Element('dim', value=[1, 1], path=path)
    nose.tools.eq_(actual, expected)

