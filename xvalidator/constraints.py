from __future__ import unicode_literals
from collections import namedtuple
import logging

import utils
from py2to3 import string_types

from xvalidator.validators import Validator, ValidationException, NCName, Name


logger = logging.getLogger(__name__)

KeyRef = namedtuple('KeyRef', 'key_name key_value ref_path')


class KeyStore(object):
    def __init__(self):
        self._key_index = {}
        self._keys = {}

    def add_key(self, key_names, target_path):
        if isinstance(key_names, list):
            key_names_list = key_names
        else:
            key_names_list = [key_names]
        for key_name in key_names_list:
            key = '%s:%s' % (key_name, target_path)
            if key in self._keys:
                raise ValidationException('Key %s does already exist.' % key,
                                          target_path)
            if not key_name in self._key_index:
                self._key_index[key_name] = [target_path]
            else:
                self._key_index[key_name].append(target_path)
            self._keys[key] = {}

    def in_keys(self, key_name, target_path):
        return '%s:%s' % (key_name, target_path) in self._keys

    def add_value(self, key_names, target_path, key_value, key_path):
        if isinstance(key_names, string_types):
            key_names_list = [key_names]
        else:
            key_names_list = key_names
        for key_name in key_names_list:
            key = '%s:%s' % (key_name, target_path)
            if self.in_keys(key_name, target_path):
                if key_value in self._keys[key]:
                    msg = 'Duplicate key value %s for %s at %s' % (key_value,
                                                                   key_name,
                                                                   key_path)
                    raise ValidationException(msg, key_value)
                self._keys[key][key_value] = key_path
                return True
        msg = 'Could not find target path %s for key name(s) %s' % (target_path,
                                                                    ', '.join(key_names_list))
        raise ValidationException(msg, key_value)

    def match_ref(self, key_name, ref_key_value):
        if not key_name in self._key_index:
            raise ValidationException('No key for %s exists' % key_name,
                                      key_name)
        for key_path in self._key_index[key_name]:
            key = '%s:%s' % (key_name, key_path)
            for key_value, instance_path in self._keys[key].items():
                if key_value == ref_key_value:
                    return instance_path
        raise ValidationException('Could not match ref %s for %s' % (
            ref_key_value, key_name), ref_key_value)

    def key_value_count(self, key_name, target_path):
        key = '%s:%s' % (key_name, target_path)
        if key in self._keys:
            return len(self._keys[key])
        return 0

    @property
    def keys(self):
        return {key: value for key, value in self._keys.items()}


class IDStore(KeyStore):
    key_name = 'ID'
    path = '/'

    def __init__(self):
        super(IDStore, self).__init__()
        super(IDStore, self).add_key(self.key_name, self.path)

    def add_id(self, key_value, key_path):
        super(IDStore, self).add_value(self.key_name, self.path,
                                       key_value, key_path)

    def match_id(self, ref_key_value):
        return super(IDStore, self).match_ref(self.key_name, ref_key_value)

    def id_count(self):
        return super(IDStore, self).key_value_count(self.key_name, self.path)


class RefStore(object):
    def __init__(self):
        self._refs = []
        self._targets = {}

    def add_key_ref(self, key_name, key_value, ref_path):
        if not key_value:
            raise ValidationException('key value is required', key_value)
        self._refs.append(KeyRef(key_name, key_value, ref_path))

    def set_target(self, ref_path, target_path):
        if ref_path in self._targets:
            raise ValidationException('Target for ref_path already exists.', ref_path)
        self._targets[ref_path] = target_path

    @property
    def refs(self):
        return [ref for ref in self._refs]

    @property
    def targets(self):
        return {ref: target for ref, target in self._targets.items()}


class IDREFStore(RefStore):
    key_name = 'IDREF'

    def add_idref(self, key_value, ref_path):
        super(IDREFStore, self).add_key_ref('ID', key_value, ref_path)


class Stores(object):
    def __init__(self):
        self.keyStore = KeyStore()
        self.uniquesStore = KeyStore()
        self.idStore = IDStore()
        self.refStore = RefStore()
        self.idrefStore = IDREFStore()


def get_value_path_stores(value, **kwargs):
    messages = dict(
        path='No path supplied.',
        store='Parameter store of type Stores expected.',
    )

    stores = kwargs['stores']
    assert isinstance(stores, Stores), messages['store']
    path = getattr(value, 'path', None)
    if 'path' in kwargs:
        path = kwargs['path']
    assert path, messages['path']
    return getattr(value, 'value', value), path, stores


class InitStores(Validator):
    """
    Creates an empty dict under
    stores.keyStore[keyName:keyTargetInstancePath]
    """
    key_names = None
    unique_names = None
    messages = dict(
        name='key names (string or list of strings) is required and can not be empty.',
        store='Parameter store of type Stores expected.',
    )

    def to_python(self, value, **kwargs):
        v, path, stores = get_value_path_stores(value, **kwargs)
        if self.key_names:
            stores.keyStore.add_key(self.key_names, path)
        if self.unique_names:
            stores.uniquesStore.add_key(self.unique_names, path)

    def build(self, *args, **kwargs):
        return super(InitStores, self).build(*args, **kwargs)


class InitKeyStore(InitStores):
    """
    Creates an empty dict under
    stores.keyStore[keyName:keyTargetInstancePath]
    """
    messages = dict(
        name='keyName (string) is required and can not be empty.',
        store='Parameter store of type Stores expected.',
    )

    def __init__(self, key_name, **kwargs):
        super(InitKeyStore, self).__init__(**kwargs)
        assert key_name and isinstance(key_name, string_types), self.messages['name']
        self.key_names = [key_name]


class InitUniqueStore(InitKeyStore):
    def __init__(self, key_name, **kwargs):
        super(InitUniqueStore, self).__init__(key_name, **kwargs)
        self.unique_names = [key_name]


class AddKeyRef(Validator):
    """
    """
    string_validator_instance = None
    refer_key_name = None
    messages = dict(
        names='%(keyNames (type list of strings or string) is is required.',
        emptyValue='Value may not be empty.',
    )

    def to_python(self, value, **kwargs):
        key_value, path, stores = get_value_path_stores(value, **kwargs)
        if self.string_validator_instance:
            string_value = self.string_validator_instance.to_python(key_value)
        else:
            string_value = key_value
        stores.refStore.add_key_ref(self.refer_key_name, string_value, path)
        return string_value

    def build(self, *args, **kwargs):
        self.default_build_value = self.refer_key_name + '0'
        return super(AddKeyRef, self).build(*args, **kwargs)


class SetupKeyRefsStore(AddKeyRef):
    """
    """
    string_validator = None
    refer_key_name = None
    messages = dict(
        names='%(keyNames (type list of strings or string) is is required.',
        emptyValue='Value may not be empty.',
    )

    def __init__(self, refer_key_name, **kwargs):
        super(SetupKeyRefsStore, self).__init__(**kwargs)
        self.refer_key_name = refer_key_name


class CheckKeys(Validator):
    """
    Determines the targetPath by removing <level>s from path.

    Looks up store[keyName:keyTargetInstancePath] for all

    keyNames and checks the dict if keyValue (element.value) is already
    present (duplicate error). If not it adds the element.value as key
    and element.path as value.
    """
    not_empty = True
    string_validator_instance = None
    key_names = None
    refer_key_name = None
    level = None
    messages = dict(
        names='%(keyNames (type list of strings or string) is is required.',
        stores='%(stores (type dict) is is required.',
        missing='%(param)s is required for CheckKeys.',
        type='%(param)s should be of type %(type)s.',
        duplicate='%(value)s is a duplicate entry for key %(key)s.',
        noMatch='Could not find match for path %(path)s.',
        stateMissing='Parameter state is required.',
        emptyValue='Value may not be empty.',
    )

    def __init__(self, **kwargs):
        super(CheckKeys, self).__init__(**kwargs)
        assert self.key_names, self.messages['names']
        if isinstance(self.key_names, list):
            assert self.key_names
            for name in self.key_names:
                assert isinstance(name, string_types)
        else:
            assert isinstance(self.key_names, string_types)
            self.key_names = [self.key_names]
        assert isinstance(self.level, int)

    def to_python(self, value, **kwargs):
        key_value, path, stores = get_value_path_stores(value, **kwargs)
        if not key_value:
            if not self.not_empty:
                return key_value
                # self.not_empty
            raise ValidationException(self.messages['emptyValue'], value)
        if self.string_validator_instance:
            string_value = self.string_validator_instance.to_python(key_value)
        else:
            string_value = key_value
        target_path = '/'.join(path.split('/')[:-self.level])
        if self.refer_key_name:
            stores.refStore.add_key_ref(self.refer_key_name, key_value, path)
        self.add_value(stores, target_path, string_value, path)
        return string_value

    def add_value(self, stores, target_path, value, path):
        if self.key_names:
            stores.keyStore.add_value(self.key_names, target_path, value, path)

    def gen_key_value(self, store, path):
        suffix = '0'
        name = ''
        target_path = '/'.join(path.split('/')[:-self.level])
        for key_name in self.key_names:
            if store.in_keys(key_name, target_path):
                name = key_name
                suffix = str(store.key_value_count(key_name, target_path))
                break
        if self.refer_key_name:
            return self.refer_key_name + suffix
        return name + suffix

    def gen_default_build_value(self, stores, path):
        return self.gen_key_value(stores.keyStore, path)

    def build(self, *args, **kwargs):
        key_value, path, stores = get_value_path_stores(None, **kwargs)
        self.default_build_value = self.gen_default_build_value(stores, path)
        return super(CheckKeys, self).build(*args, **kwargs)


class CheckUniques(CheckKeys):
    not_empty = False
    key_names = None

    def add_value(self, stores, target_path, value, path):
        if self.key_names:
            stores.uniquesStore.add_value(self.key_names, target_path, value, path)

    def gen_default_build_value(self, stores, path):
        return super(CheckUniques, self).gen_key_value(stores.uniquesStore, path)


class KeyName(CheckKeys):
    """

    """
    not_empty = True
    store_name = 'keyStore'
    string_validator_instance = Name()



class UniqueName(CheckUniques):
    """
    A UniqueName is of type Name and may be empty.
    """
    not_empty = False
    string_validator_instance = Name()



class ID(NCName):
    """
    The type ID is used for an attribute that uniquely identifies an element
    in an XML document. An ID value must conform to the rules for an NCName.
    This means that it must start with a letter or underscore, and can only
    contain letters, digits, underscores, hyphens, and periods. ID values
    must be unique within an XML instance, regardless of the attribute's name
    or its element name.
    """
    not_empty = True

    def to_python(self, value, **kwargs):
        key_value, path, stores = get_value_path_stores(value, **kwargs)
        string_value = super(ID, self).to_python(key_value, **kwargs)
        stores.idStore.add_id(string_value, path)
        return value

    def build(self, *args, **kwargs):
        key_value, path, stores = get_value_path_stores(None, **kwargs)
        self.default_build_value = 'testId' + str(stores.idStore.id_count())
        return super(ID, self).build(*args, **kwargs)


class IDREF(NCName):
    """
    The type ID is used for an attribute that uniquely identifies an element
    in an XML document. An ID value must conform to the rules for an NCName.
    This means that it must start with a letter or underscore, and can only
    contain letters, digits, underscores, hyphens, and periods. ID values
    must be unique within an XML instance, regardless of the attribute's name
    or its element name.
    """
    default_build_value = 'testId0'
    not_empty = True

    def to_python(self, value, **kwargs):
        key_value, path, stores = get_value_path_stores(value, **kwargs)
        string_value = super(IDREF, self).to_python(value, **kwargs)
        stores.idrefStore.add_idref(string_value, path)
        return value


def match_refs(stores):
    def match_store_refs(key_store, ref_store):
        for ref in ref_store.refs:
            instance_path = key_store.match_ref(ref.key_name, ref.key_value)
            ref_store.set_target(ref.ref_path, instance_path)
            logger.debug('Successfully matched "%s/%s", got: %r'
                         % (ref.key_name, ref.key_value, instance_path))

    match_store_refs(stores.keyStore, stores.refStore)
    match_store_refs(stores.idStore, stores.idrefStore)
