from __future__ import unicode_literals
from collections import OrderedDict, defaultdict
from copy import copy

import nose

from xvalidator.element import Element, NameSpace, create_element, \
    get_result_tag, Document, create_document


nameSpaces = [
    NameSpace(prefix='xsi', uri='http://www.w3.org/2001/XMLSchema-instance'),
    NameSpace(prefix='spirit', uri='http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'),
    NameSpace(prefix='', uri='http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'),
]


def test_element_pass():
    el = Element('test')
    assert el.tag == 'test'


def test_element_repr():
    id_string = str('ID42')
    actual = repr(Element('tagName', value=[1, 2, 3],
                          attributes=dict(id=id_string), path='/root-0,name'))
    expected = 'Element(tag=\'tagName\', attributes={\'id\': \'ID42\'}, ' \
               'path="/root-0,name", value=[1, 2, 3])'
    nose.tools.eq_(actual, str(expected))


def test_element_str():
    actual = str(Element('tagName', value=[1, 2, 3],
                         attributes=dict(id='ID42'), path='/root-0,name'))
    nose.tools.eq_(actual, '<tagName>')


def test_get_result_key_pass():
    actual = get_result_tag('spirit:name')
    nose.tools.eq_(actual, 'spirit:name')


def test_create_element_root_only():
    el = create_element('root', {}, nameSpaces)
    nose.tools.eq_(el, Element('root', value=[], path='/root-0,'))


def test_create_element_attribute_text_pass():
    value = OrderedDict([('text', OrderedDict([('@attr', '42'),
                                                ('#text', 'root value')]))])
    el = create_element('root', value, nameSpaces)
    nose.tools.eq_(el, Element(tag='root', path="/root-0,", value=[
        Element(tag='text', attributes=OrderedDict([('attr', '42')]),
                path="/root-0,/text-0,", value='root value')]))


register = OrderedDict([('@id', 'ID6'), ('name', 'reg6'),
                        ('addressOffset', '0'),
                        ('size', '2'),
                        ('access', 'writeOnce'),
                        ('reset', OrderedDict([('value', '0')]))])


def test_create_element_one_level():
    el = create_element('register', register, nameSpaces)
    register_element = Element(tag='register', attributes=OrderedDict([
        ('id', 'ID6')]), path="/register-0,reg6", value=[
        Element(tag='name', path="/register-0,reg6/name-0,", value='reg6'),
        Element(tag='addressOffset', path="/register-0,reg6/addressOffset-0,",
                value='0'),
        Element(tag='size', path="/register-0,reg6/size-0,",
                value='2'),
        Element(tag='access', path="/register-0,reg6/access-0,",
                value='writeOnce'),
        Element(tag='reset', path="/register-0,reg6/reset-0,",
                value=[
                    Element(tag='value', path="/register-0,reg6/reset-0,/value-0,",
                            value='0')])])
    nose.tools.eq_(el, register_element)


def test_create_element_two_levels():
    register_copy = copy(register)
    field10 = OrderedDict(
        [('@id', 'ID10'), ('name', 'field10'), ('bitOffset', '0'), ('bitWidth', '2'), ('volatile', 'false')])
    field11 = OrderedDict(
        [('@id', 'ID11'), ('name', 'field11'), ('bitOffset', '2'), ('bitWidth', '4'), ('volatile', 'true')])
    register_copy['field'] = [field10, field11]
    el = create_element('register', register_copy, nameSpaces)
    expected = [
        Element(tag='field', attributes=OrderedDict([('id', 'ID10')]), path="/register-0,reg6/field-0,field10",
                value=[
                    Element(tag='name', path="/register-0,reg6/field-0,field10/name-0,", value='field10'),
                    Element(tag='bitOffset', path="/register-0,reg6/field-0,field10/bitOffset-0,", value='0'),
                    Element(tag='bitWidth', path="/register-0,reg6/field-0,field10/bitWidth-0,", value='2'),
                    Element(tag='volatile', path="/register-0,reg6/field-0,field10/volatile-0,", value='false')]),
        Element(tag='field', attributes=OrderedDict([('id', 'ID11')]), path="/register-0,reg6/field-1,field11",
                value=[
                    Element(tag='name', path="/register-0,reg6/field-1,field11/name-0,", value='field11'),
                    Element(tag='bitOffset', path="/register-0,reg6/field-1,field11/bitOffset-0,", value='2'),
                    Element(tag='bitWidth', path="/register-0,reg6/field-1,field11/bitWidth-0,", value='4'),
                    Element(tag='volatile', path="/register-0,reg6/field-1,field11/volatile-0,", value='true')])]
    nose.tools.eq_(el.value[5:], expected)


def test_create_element_stats():
    register_copy = copy(register)
    field10 = OrderedDict([
        ('@id', 'ID10'), ('name', 'field10'), ('bitOffset', '0'),
        ('bitWidth', '2'), ('volatile', 'false')])
    field11 = OrderedDict([
        ('@id', 'ID11'), ('name', 'field11'), ('bitOffset', '2'),
        ('bitWidth', '4'), ('volatile', 'true')])
    register_copy['field'] = [field10, field11]
    stats = defaultdict(int)
    create_element('register', register_copy, nameSpaces, stats=stats)
    expected_stats = {'reset': 1, 'bitOffset': 2, 'name': 3, 'bitWidth': 2,
                      'field.@id': 2, 'register.@id': 1, 'register': 1,
                      'addressOffset': 1, 'value': 1, 'access': 1, 'field': 2,
                      'volatile': 2, 'size': 1}
    nose.tools.eq_(stats, expected_stats)


def test_create_element_stats_simple_value_list():
    stats = defaultdict(int)
    test = OrderedDict([('multiple', [1, 2, 3])])
    create_element('test', test, nameSpaces, path='/', stats=stats)
    nose.tools.eq_(stats, {'multiple': 1, 'test': 1})


def test_create_document():
    register_copy = copy(register)
    register_copy['@xmlns'] = 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'
    field10 = OrderedDict([
        ('@id', 'ID10'), ('name', 'field10'), ('bitOffset', '0'),
        ('bitWidth', '2'), ('volatile', 'false')])
    field11 = OrderedDict([
        ('@id', 'ID11'), ('name', 'field11'), ('bitOffset', '2'),
        ('bitWidth', '4'), ('volatile', 'true')])
    register_copy['field'] = [field10, field11]
    doc = create_document('test_elements.py: register', OrderedDict(
        [('register', register_copy)]))
    expected_stats = {'reset': 1, 'bitOffset': 2, 'name': 3, 'bitWidth': 2,
                      'field.@id': 2, 'register.@id': 1, 'register': 1,
                      'addressOffset': 1, 'value': 1, 'access': 1, 'field': 2,
                      'volatile': 2, 'size': 1}
    nose.tools.eq_(doc.stats, expected_stats)


def test_element_to_dict_pass():
    element = Element('test', value=False)
    actual = element.to_dict
    nose.tools.eq_(actual, 'false')


def test_element_to_dict_list_pass():
    element = Element('test', value=[1, 2.0, 'name'])
    actual = element.to_dict
    nose.tools.eq_(actual, ['1', '2.0', 'name'])


def test_element_to_dict_attribute_no_value_pass():
    element = Element('test', attributes={'valid': False})
    actual = element.to_dict
    nose.tools.eq_(actual, OrderedDict([('@valid', 'false')]))


def test_element_to_dict_attribute_value_empty_list_pass():
    element = Element('test', value=[], attributes={'valid': False})
    actual = element.to_dict
    nose.tools.eq_(actual, OrderedDict([('@valid', 'false')]))


def test_element_to_dict_id_attribute_pass():
    element = Element('test', value=True, attributes={'id': 'ID42'})
    actual = element.to_dict
    nose.tools.eq_(actual, OrderedDict([('@id', 'ID42'), ('#text', 'true')]))


def test_element_to_dict_three_levels_mix_ns_prefix_pass():
    level2 = Element('post:level2', value='level2Name')
    level1 = Element('pre:level1', value=[level2])
    root = Element('parent', value=[level1])
    actual = root.to_dict
    nose.tools.eq_(actual, OrderedDict([
        ('pre:level1', OrderedDict([('post:level2', 'level2Name')]))]))


def test_element_to_dict_two_levels_three_children_pass():
    child0 = Element('pre:child', value='childName1')
    child1 = Element('pre:child', value='childName2')
    child2 = Element('pre:child', value='childName3')
    parent = Element('pre:parent', value=[child0, child1, child2])
    actual = parent.to_dict
    nose.tools.eq_(actual, OrderedDict([
        ('pre:child', ['childName1', 'childName2', 'childName3'])]))


def test_document_to_dict_two_levels_three_children_pass():
    child0 = Element('xsi:child', value='childName1')
    child1 = Element('xsi:child', value='childName2')
    child2 = Element('xsi:child', value='childName3')
    root = Element('test:parent', value=[child0, child1, child2])
    doc = Document('test', [nameSpaces[0]], root)
    actual = doc.to_dict
    nose.tools.eq_(actual, OrderedDict([
        ('test:parent', OrderedDict([
            ('@xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
            ('xsi:child', ['childName1', 'childName2', 'childName3'])
        ]))]))


def test_document_to_dict_two_levels_empty_ns_prefix_pass():
    child = Element('child', value='childName1')
    root = Element('prefix:parent', value=[child])
    doc = Document('test', [nameSpaces[2]], root)
    actual = doc.to_dict
    nose.tools.eq_(actual, OrderedDict([
        ('prefix:parent', OrderedDict([
            ('@xmlns', 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'),
            ('child', 'childName1')
        ]))]))


def test_document_to_dict_two_levels_round_trip_pass():
    p = '/xsi:parent-0,/xsi:child-'
    child = Element('xsi:child', value='childName1', path=p + '0,')
    root = Element('xsi:parent', value=[child], path='/xsi:parent-0,')
    stats = defaultdict(int)
    stats['xsi:parent'] = 1
    stats['xsi:child'] = 1
    doc = Document('test', [nameSpaces[0]], root, stats=stats)
    xml_dict = doc.to_dict
    doc_new = create_document('test', xml_dict)
    nose.tools.eq_(doc.__dict__.items(), doc_new.__dict__.items())


def test_document_to_dict_two_levels_top_attribute_round_trip_pass():
    p = '/xsi:parent-0,/xsi:child-'
    child = Element('xsi:child', value='childName1', path=p + '0,')
    root = Element('xsi:parent', value=[child], path='/xsi:parent-0,')
    stats = defaultdict(int)
    stats['xsi:parent'] = 1
    stats['xsi:child'] = 1
    stats['xsi:parent.@id'] = 1
    doc = Document('test', [nameSpaces[0]], root, stats=stats,
                   attributes=OrderedDict([('id', 'ID42')])
        )
    xml_dict = doc.to_dict
    doc_new = create_document('test', xml_dict)
    nose.tools.eq_(doc.__dict__.items(), doc_new.__dict__.items())
