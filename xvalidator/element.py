from collections import namedtuple, OrderedDict, defaultdict
import logging

from xvalidator import utils


__author__ = 'bernd'

logger = logging.getLogger(__name__)

NameSpace = namedtuple('NameSpace', 'prefix uri')


def _value_to_string(value):
    if not value is None:
        if isinstance(value, bool):
            if value:
                return 'true'
            return 'false'
        return str(value)


class Element(utils.CommonEqualityMixin):
    def __init__(self, tag, value=None, attributes=None,
                 path='', ns_prefix=''):
        self.tag = tag
        self.value = value
        # strValue = value if isinstance(value, six.string_types) else None
        # self.displayValue = displayValue if not displayValue is None else strValue
        self.attributes = attributes
        #        if attributes:
        #            self.displayAttributes = {key: value
        #                                      for key, value in attributes.items()}
        #        else:
        #            self.displayAttributes = None
        self.path = path
        self.ns_prefix = ns_prefix
        self.isValidated = False

    def __repr__(self):
        r = "Element(tag='%s'" % self.tag
        if self.attributes:
            r += ", attributes=%r" % self.attributes
        if self.path:
            r += ', path="%s"' % self.path
        if self.ns_prefix:
            r += ", ns_prefix=%s" % self.ns_prefix
        return r + ", value=%r)" % self.value

    def __str__(self):
        return '<%s>' % self.tag

    @property
    def to_dict(self):
        ns_prefix_colon = self.ns_prefix + ':' if self.ns_prefix else ''
        result = OrderedDict()
        if self.attributes:
            for key, value in self.attributes.items():
                result['@%s%s' % (ns_prefix_colon, key)] = _value_to_string(value)
        if isinstance(self.value, list):
            if self.value and isinstance(self.value[0], Element):
                for child in self.value:
                    child_prefix = child.ns_prefix + ':' if child.ns_prefix else ''
                    key = '%s%s' % (child_prefix, child.tag)
                    if key in result:
                        if isinstance(result[key], list):
                            result[key].append(child.to_dict)
                        else:
                            result[key] = [result[key],
                                           child.to_dict]
                    else:
                        result[key] = child.to_dict
                return result
            value = [_value_to_string(item) for item in self.value]
        else:
            value = _value_to_string(self.value)
        if result:
            if value is None or value == '':
                return result
            result['#text'] = _value_to_string(value)
            return result
        return value


def check_name_space_prefix(key, name_spaces):
    no_at_key = key.replace('@', '')
    if ':' in no_at_key:
        ns_prefix = no_at_key.split(':')[0]
    else:
        ns_prefix = ''
    found = False
    for index, name_space in enumerate(name_spaces):
        if ns_prefix == name_space.prefix:
            found = True
    if not found:
        utils.error(logger, 'Could not find ns_prefix for key: "%s"' % key)
    return ns_prefix


def get_result_tag(key):
    result_key = key.replace('@', '')
    if ':' in result_key:
        result_key = result_key.split(':')[1]
    return result_key


def create_element(tag, value_dict, name_spaces, path='', instance_index=0,
                   stats=None, is_root=False):
    """
    """
    ns_prefix = ''
    if not is_root:
        ns_prefix = check_name_space_prefix(tag, name_spaces)
    parent_tag = get_result_tag(tag)
    value_dict_keys = {
        (key.split(':')[1] if ':' in key else key): key
        for key in value_dict.keys()}
    name = value_dict[value_dict_keys['name']] if 'name' in value_dict_keys else ''
    new_path = path + '/%s-%d,%s' % (parent_tag, instance_index, name)
    element_value = []
    attributes = None
    for child_key, child_value in value_dict.items():
        if child_key == '#text':
            element_value = value_dict['#text']
        else:
            is_attribute = child_key[0] == '@'
            child_tag = get_result_tag(child_key)
            child_path = new_path + '/' + child_tag + '-0,'
            child_ns_prefix = check_name_space_prefix(child_key, name_spaces)
            if is_attribute:
                if not attributes:
                    attributes = OrderedDict()
                attributes[child_tag] = child_value
                if not stats is None:
                    stats['%s.@%s' % (tag, child_tag)] += 1
            elif isinstance(child_value, OrderedDict):
                element_value.append(
                    create_element(child_key, child_value, name_spaces, new_path, stats=stats))
            elif isinstance(child_value, list) and child_value:
                if isinstance(child_value[0], OrderedDict):  # list of children
                    element_value.extend([create_element(child_key, item, name_spaces,
                                         new_path, instance_index=index, stats=stats)
                                         for index, item in enumerate(child_value)])
                else:  # list of values
                    element_value.append(Element(
                        tag=child_tag, value=child_value,
                        attributes=attributes, path=child_path, ns_prefix=child_ns_prefix))
                    if not stats is None:
                        stats[child_key] += 1
            else:  # single value
                element_value.append(Element(
                    tag=child_tag, value=child_value, path=child_path,
                    ns_prefix=child_ns_prefix))
                if not stats is None:
                    stats[child_key] += 1
    if not stats is None:
        stats[tag] += 1
    return Element(tag=parent_tag, value=element_value,
                   attributes=attributes, path=new_path, ns_prefix=ns_prefix)


class Document(utils.CommonEqualityMixin):
    def __init__(self, source, name_spaces, root_element, attributes=None,
                 stats=None):
        self.source = source
        self.name_spaces = name_spaces
        self.root_element = root_element
        self.attributes = attributes
        self.stats = stats if not stats is None else defaultdict(int)

    @property
    def to_dict(self):
        def ns_to_attribute(name_space):
            if name_space.prefix:
                return '@xmlns:%s' % name_space.prefix, name_space.uri
            return '@xmlns', name_space.uri

        result = OrderedDict()
        root = self.root_element.to_dict
        root_attr = [ns_to_attribute(ns) for ns in self.name_spaces]
        if self.attributes:
            root_attr.extend([('@' + key, value)
                              for key, value in self.attributes.items()])
        result[self.root_element.tag] = OrderedDict(root_attr + list(root.items()))
        return result


def create_document(source, xml_dict):
    name_spaces = []
    assert len(xml_dict) == 1
    root_tag = list(xml_dict.keys())[0]
    xml_root = OrderedDict()
    attributes = OrderedDict()
    stats = defaultdict(int)
    for key, value in list(xml_dict.values())[0].items():
        if key[0] == '@':
            if '@xmlns' in key:
                prefix = key[7:] if ':' in key else ''
                name_spaces.append(NameSpace(prefix=prefix, uri=value))
            else:
                attributes[key[1:]] = value
                stats['%s.%s' % (root_tag, key)] += 1
        else:
            xml_root[key] = value
    root_element = create_element(root_tag, xml_root, name_spaces, stats=stats,
                                  is_root=True)
    attributes_arg = attributes if attributes else None
    return Document(source=source, name_spaces=name_spaces, attributes=attributes_arg,
                    root_element=root_element, stats=stats)
