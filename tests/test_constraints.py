import nose
from nose.tools import raises

from xvalidator import constraints
from xvalidator.element import Element
from xvalidator.validators import ValidationException


__author__ = 'bernd'


@raises(ValidationException)
def test_init_key_store_add_duplicate_key_name_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('TestKeys')
    path='/root-0,'
    ks.to_python(None, path=path, stores=stores)
    ks.to_python(None, path=path, stores=stores)


def test_init_unique_store_pass():
    stores = constraints.Stores()
    ks = constraints.InitUniqueStore('TestUnique')
    path = '/root-0,/test'
    ks.to_python(None, path=path, stores=stores)
    nose.tools.eq_(stores.keyStore.keys, {'TestUnique:/root-0,/test': {}})


def test_init_key_store_pass():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('TestKey')
    path = '/root-0,/test'
    ks.to_python(None, path=path, stores=stores)
    nose.tools.eq_(stores.keyStore.keys, {'TestKey:/root-0,/test': {}})


def test_key_store_add_value_pass():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('TestKey')
    ks.to_python(None, path='/', stores=stores)
    stores.keyStore.add_value('TestKey', '/', 'key_value', '/ads/cgfh')
    expected = {'TestKey:/': {'key_value': '/ads/cgfh'}}
    nose.tools.eq_(stores.keyStore.keys, expected)


def test_check_ids_add_id_pass():
    stores = constraints.Stores()
    ks = constraints.ID()
    el = Element('test', path='/el42-0,', attributes=dict(id='ID42'))
    id_element = Element('id', path=el.path + '@id', value=el.attributes['id'])
    ks.to_python(id_element, stores=stores)
    stores.idStore.add_id('key_value', '/ads/cgfh')
    expected = {'ID:/': {'key_value': '/ads/cgfh', 'ID42': '/el42-0,@id'}}
    nose.tools.eq_(stores.idStore.keys, expected)


def test_init_key_store_two_keys_pass():
    stores = constraints.Stores()
    ks0 = constraints.InitKeyStore('TestKey')
    path = '/root-0,/test-0,'
    el = Element('test', path=path)
    ks0.to_python(el, path=el.path, stores=stores)
    ks1 = constraints.InitKeyStore('TestKey')
    path = '/root-0,/test-1,'
    ks1.to_python(None, path=path, stores=stores)
    expected = {'TestKey:/root-0,/test-1,': {}, 'TestKey:/root-0,/test-0,': {}}
    nose.tools.eq_(stores.keyStore.keys, expected)


def test_setup_key_refs_store_pass():
    stores = constraints.Stores()
    ks = constraints.SetupKeyRefsStore('TestKeyRef')
    path = '/root-0,/test'
    el = Element('test', value='refName', path=path)
    ks.to_python(el, stores=stores)
    nose.tools.eq_(stores.refStore.refs, [constraints.KeyRef(key_name='TestKeyRef',
                                                      key_value='refName', ref_path='/root-0,/test')])


@raises(ValidationException)
def test_setup_key_refs_store_value_none_fail():
    stores = constraints.Stores()
    ks = constraints.SetupKeyRefsStore('TestKeyRef')
    ks.to_python(None, path='/', stores=stores)


@raises(ValidationException)
def test_setup_key_refs_store_value_empty_fail():
    stores = constraints.Stores()
    ks = constraints.SetupKeyRefsStore('TestKeyRef')
    el = Element('test', value='', path='/')
    ks.to_python(el.value, path=el.path, stores=stores)


@raises(AssertionError)
def test_init_key_store_no_key_fail():
    constraints.InitKeyStore('')


def test_check_keys_single_key_pass():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names='FieldKey', level=1)
    field = Element('field', value='field22', path=path + '/field-2,field22')
    nose.tools.eq_(ck.to_python(field.value, path=field.path, stores=stores), 'field22')


def test_check_uniques_empty_value_pass():
    stores = constraints.Stores()
    ks = constraints.InitUniqueStore('FieldKey')
    path = "/register-0,reg6"
    el = Element('reg', path=path)
    ks.to_python(el, stores=stores)
    ck = constraints.CheckUniques(key_names='FieldKey', level=1)
    field = Element('field', value=None, path=path + '/field-2,field22')
    nose.tools.eq_(ck.to_python(field.value, path=field.path, stores=stores), None)


def test_check_uniques_single_key_pass():
    stores = constraints.Stores()
    ks = constraints.InitUniqueStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckUniques(key_names='FieldKey', level=1)
    field = Element('field', value='field22', path=path + '/field-2,field22')
    actual = ck.to_python(field.value, path=field.path, stores=stores)
    nose.tools.eq_(actual, 'field22')


@raises(ValidationException)
def test_check_uniques_duplicate_value_fail():
    stores = constraints.Stores()
    ks = constraints.InitUniqueStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckUniques(key_names='FieldKey', level=1)
    field0 = Element('field', value='field22', path=path + '/field-2,field22')
    field1 = Element('field', value='field22', path=path + '/field-12,field22')
    ck.to_python(field0, stores=stores)
    ck.to_python(field1, stores=stores)


@raises(ValidationException)
def test_check_keys_duplicate_value_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names='FieldKey', level=1)
    field0 = Element('field', value='field22', path=path + '/field-2,field22')
    field1 = Element('field', value='field22', path=path + '/field-12,field22')
    nose.tools.eq_(ck.to_python(field0, stores=stores), 'field22')
    ck.to_python(field1, stores=stores)


@raises(ValidationException)
def test_check_keys_empty_value_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names='FieldKey', level=1)
    field = Element('field', path=path + '/field-2,field22')
    ck.to_python(field, stores=stores)


def test_check_keys_three_keys_pass():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('FieldKey')
    path = "/register-0,reg6"
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names=['OtherKey', 'FieldKey',
                                          'YetAnotherKey'], level=1)
    field = Element('field', value='field22', path=path + '/field-2,field22')
    expected = {'FieldKey:/register-0,reg6':
                    {'field22': '/register-0,reg6/field-2,field22'}}
    ck.to_python(field, stores=stores)
    nose.tools.eq_(stores.keyStore.keys, expected)


@raises(AssertionError)
def test_check_keys_no_level_fail():
    constraints.CheckKeys(key_names=['OtherKey', 'FieldKey', 'YetAnotherKey'],
        level=None)


@raises(AssertionError)
def test_check_keys_level_type_fail():
    constraints.CheckKeys(key_names=['OtherKey', 'FieldKey'], level='55')


@raises(AssertionError)
def test_check_keys_wrong_keynames_type_fail():
    constraints.CheckKeys(key_names=13, level=2)


@raises(ValidationException)
def test_check_keys_path_mismatch_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('FieldKey')
    path = "/register-0,reg6"
    el = Element('reg', path=path)
    ks.to_python(el, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names='FieldKey', level=1)
    field = Element('field', value='field22', path='/field-2,field22')
    ck.to_python(field, stores=stores)


def test_check_ids_single_pass():
    stores = constraints.Stores()
    ci = constraints.ID()
    ci.to_python('ID42', path='/field-0,@id', stores=stores)
    expected = {'ID:/': {'ID42': '/field-0,@id'}}
    nose.tools.eq_(stores.idStore.keys, expected)


def test_set_id_ref_store_pass():
    idr = constraints.IDREFStore()
    idr.add_idref('key_value', 'ref_path')
    expected = [constraints.KeyRef(key_name='ID',
        key_value='key_value', ref_path='ref_path')]
    nose.tools.eq_(idr.refs, expected)


def test_check_idref_single_pass():
    stores = constraints.Stores()
    cr = constraints.IDREF()
    cr.to_python('ID42', path='/ref-0,/for-0,/field-0,', stores=stores)
    expected = constraints.KeyRef(key_name='ID', key_value='ID42',
        ref_path='/ref-0,/for-0,/field-0,')
    nose.tools.eq_(stores.idrefStore.refs[0], expected)


def test_set_target_pass():
    rs = constraints.RefStore()
    rs.set_target('ref_path', 'target_path')
    nose.tools.eq_(rs.targets, {'ref_path': 'target_path'})


@raises(ValidationException)
def test_set_target_duplicate_target_fail():
    rs = constraints.RefStore()
    rs.set_target('ref_path', 'target_path')
    rs.set_target('ref_path', 'target_path')


@raises(ValidationException)
def test_match_ref_nonexistent_key_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('key_name')
    ks.to_python(None, path='/', stores=stores)
    stores.keyStore.match_ref('wrong_name', 'field22')


@raises(ValidationException)
def test_match_ref_nonexistent_key_name_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('key_name')
    ks.to_python(None, path='/', stores=stores)
    stores.keyStore.match_ref('key_name', 'field22')


def test_match_ref_pass():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('key_name')
    path = '/root-0,'
    ks.to_python(None, path=path, stores=stores)
    ck = constraints.CheckKeys(key_names=['OtherKey', 'key_name'], level=1)
    field = Element('field', value='field22', path=path + '/field-2,field22')
    ck.to_python(field.value, path=field.path, stores=stores)
    instance_path = stores.keyStore.match_ref('key_name', 'field22')
    nose.tools.eq_(instance_path, path + '/field-2,field22')


def test_match_id_pass():
    stores = constraints.Stores()
    path = '/root-0,'
    ck = constraints.ID()
    field = Element('field', value='field22', path=path + '/field-2,field22')
    ck.to_python(field, stores=stores)
    instance_path = stores.idStore.match_id('field22')
    nose.tools.eq_(instance_path, path + '/field-2,field22')


@raises(ValidationException)
def test_match_ref_key_value_not_found_fail():
    stores = constraints.Stores()
    ks = constraints.InitKeyStore('key_name')
    ks.to_python(None, path='/', stores=stores)
    stores.keyStore.match_ref('key_name', 'field220')


def test_match_refs_pass():
    stores = constraints.Stores()
    root_element = Element('root', value=None, path='/component-0,test')
    key_element = Element('name', value='myMemoryMap',
                          path='/component-0,test/memoryMap-0,myMemoryMap/name-0,')
    ref_element = Element('memoryMapRef', value='myMemoryMap',
                          path='/component-0,test/busInterface-0,/memoryMapRef-0,@memoryMapRef')
    constraints.InitKeyStore('memoryMapKey').to_python(
        root_element, stores=stores)
    constraints.CheckKeys(key_names='memoryMapKey', level=2).to_python(
        key_element, stores=stores)
    kr = constraints.SetupKeyRefsStore('memoryMapKey')
    kr.to_python(ref_element, stores=stores)
    constraints.match_refs(stores)
    targets = {'/component-0,test/busInterface-0,/memoryMapRef-0,@memoryMapRef':
                   '/component-0,test/memoryMap-0,myMemoryMap/name-0,'}
    nose.tools.eq_(stores.refStore.targets, targets)


@raises(ValidationException)
def test_match_refs_value_not_found_fail():
    stores = constraints.Stores()
    root_element = Element('root', value=None, path='/component-0,test')
    ref_element = Element('memoryMapRef', value='myMemoryMap',
                          path='/component-0,test/busInterface-0,/memoryMapRef-0,@memoryMapRef')
    constraints.InitKeyStore('memoryMapKey').to_python(root_element, path=root_element.path, stores=stores)
    kr = constraints.SetupKeyRefsStore('memoryMapKey')
    kr.to_python(ref_element, stores=stores)
    constraints.match_refs(stores)


def test_match_idref_to_id_single_pass():
    stores = constraints.Stores()
    ci = constraints.ID()
    cr = constraints.IDREF()
    ci.to_python('ID42', path='/field-0,@id', stores=stores)
    cr.to_python('ID42', path='/ref-0,/for-0,/field-0,', stores=stores)
    constraints.match_refs(stores)
    expected = {'/ref-0,/for-0,/field-0,': '/field-0,@id'}
    nose.tools.eq_(stores.idrefStore.targets, expected)


def test_unique_name_two_keys_pass():
    ks = constraints.InitUniqueStore('Key2')
    stores = constraints.Stores()
    root_path = '/root-0,'
    ks.to_python(None, path=root_path, stores=stores)
    u_name = constraints.UniqueName(key_names='Key1 Key2'.split(), level=1)
    key_path = root_path + '/child-1,prefixed:name'
    actual = u_name.to_python('prefixed:name', path=key_path, stores=stores)
    nose.tools.eq_(actual, 'prefixed:name')


def test_key_name_two_keys_pass():
    ks = constraints.InitKeyStore('Key2')
    stores = constraints.Stores()
    root_path = '/root-0,'
    ks.to_python(None, path=root_path, stores=stores)
    u_name = constraints.KeyName(key_names='Key1 Key2'.split(), level=1)
    key_path = root_path + '/child-1,prefixed:name'
    actual = u_name.to_python('prefixed:name', path=key_path, stores=stores)
    nose.tools.eq_(actual, 'prefixed:name')


def test_key_sub_class_name_two_keys_pass():
    class TestKeyName(constraints.KeyName):
        key_names = 'Key1 Key2'.split()
        refer_key_name = 'referKey'
        level = 1

    ks = constraints.InitKeyStore('Key2')
    stores = constraints.Stores()
    root_path = '/root-0,'
    ks.to_python(None, path=root_path, stores=stores)
    u_name = TestKeyName()
    key_path = root_path + '/child-1,prefixed:name'
    actual = u_name.to_python('prefixed:name', path=key_path, stores=stores)
    nose.tools.eq_(stores.refStore.refs, [
        constraints.KeyRef(key_name='referKey', key_value='prefixed:name', ref_path='/root-0,/child-1,prefixed:name')])


