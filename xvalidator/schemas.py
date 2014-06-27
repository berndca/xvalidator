from collections import namedtuple, OrderedDict
import logging

from xvalidator.element import Element
from xvalidator import utils
from xvalidator.validators import Validator, ValidationException


__author__ = 'bernd'

logger = logging.getLogger(__name__)

SELF = namedtuple('SELF', '')


class ElementSchema(Validator):
    """

    """
    _tag = ''
    validator = None
    minOccurs = 0
    unbounded = False
    default = None
    attributes = None

    messages = dict(
        extraArg='Found unexpected argument %s',
        invalidArg='Invalid argument type for %(tag)s arg: %(arg)s. %(item)r',
    )

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.tag)

    def __init__(self, tag, **kwargs):
        super(ElementSchema, self).__init__(**kwargs)
        expected_attrs = {"_tag", "validator", "minOccurs", "unbounded",
                          "default", "attributes"}
        for attrName in kwargs.keys():
            assert attrName in expected_attrs, self.messages['extraArg'] % attrName
        self._tag = tag
        if self.validator:
            msg = 'validator:%r must be an instance of xvalidator.Validator' % self.validator
            assert isinstance(self.validator, Validator), msg
        self.attributes = self.__check_schema_args__('attributes', kwargs)

    def __check_schema_args__(self, arg_name, new_attrs):
        result = []
        arg = new_attrs.get(arg_name, None)
        if arg:
            if isinstance(arg, list):
                arg_list = arg
            else:
                arg_list = [arg]
            for argItem in arg_list:
                assert isinstance(argItem, (Validator, list)), \
                    self.messages['invalidArg'] % dict(tag=self.tag, arg=arg_name,
                                                       item=repr(argItem))
                result.append(argItem)
        return result

    def _validate(self, validator, value, value_type, **kwargs):
        if validator is None:
            return value
        try:
            result = validator.to_python(value, **kwargs)
        except ValidationException as e:
            path = kwargs['path']
            msg = 'Error validating %s in "%s": %s got: %r' % (
                value_type, path, e._msg, value)
            utils.error(logger, msg)
        else:
            logger.debug('Successfully validated "%s", got: %r'
                         % (value_type, result))
            return result

    def _validate_attributes(self, element, **kwargs):
        validated_attributes = OrderedDict()
        attributes = element.attributes
        if attributes:
            expected_attributes = set([validator.tag
                                       for validator in self.attributes
                                       if validator.tag[-1] != '*'])
            extra_attribute_keys = set(attributes.keys()) - expected_attributes
            validators = OrderedDict()
            for validator in self.attributes:
                if validator.tag in attributes.keys():
                    validators[validator.tag] = validator
            if extra_attribute_keys:
                allow_extra_attributes = any(validator.tag[-1] == '*'
                                             for validator in self.attributes)
                if allow_extra_attributes:
                    for extra_attribute_name in extra_attribute_keys:
                        validated_attributes[extra_attribute_name] = attributes[extra_attribute_name]
                else:
                    utils.error(logger, 'Found unexpected attributes: "%s" in "%s".' % (
                        ', '.join(extra_attribute_keys), element.path))
            for tag in validators.keys():
                if tag in expected_attributes:
                    if validators[tag].validator is None:
                        validated_attributes[tag] = attributes[tag]
                    else:
                        kwargs.update(path=element.path + '@%s' % tag)
                        validated_attributes[tag] = self._validate(
                            validators[tag].validator,
                            attributes[tag], '%s.@%s' % (element.tag, tag),
                            **kwargs)
            return validated_attributes

    @property
    def tag(self):
        return self._tag

    def to_python(self, element, **kwargs):
        assert isinstance(element, Element), 'Argument element should be of type Element, got %r' % element
        kwargs.update(path=element.path)
        if isinstance(element.value, list):
            if element.value and isinstance(element.value[0], Element):
                element.value = self._validate(self.validator, element.value,
                                               'Element %s' % element.tag, **kwargs)
            else:
                element.value = [self._validate(self.validator, item,
                                                'Element %s' % element.tag, **kwargs)
                                 for item in element.value]
        elif self.validator:
            if element.value is None and self.minOccurs == 0:
                logger.debug('Ignoring empty element "%s".' % element.tag)
            else:
                element.value = self._validate(self.validator, element.value,
                                               'Element %s' % element.tag, **kwargs)
        element.attributes = self._validate_attributes(element, **kwargs)
        element.isValidated = True
        return element

    def build(self, *args, **kwargs):
        path = kwargs.get('path')
        if self.validator:
            value = self.validator.build(*args, **kwargs)
        else:
            value = None
        attributes = OrderedDict()
        for attr in self.attributes:
            if attr.validator:
                attributes[attr.tag] = attr.validator.build(*args, **kwargs)
        return self.to_python(Element(self.tag, value=value, attributes=attributes, path=path))


class Choice(utils.CommonEqualityMixin):
    """

    """

    def __init__(self, options, required=True):
        assert isinstance(options, list)
        self.options = [option for option in options]
        self._flat_options = self._flat_options_dict()
        self.all_keys_set = set(self._flat_options.keys())
        self.required_keys_sets = self.choice_to_key_sets(True)
        self.optional_keys_sets = self.choice_to_key_sets(False)
        self.required = required

    def __str__(self):
        return 'Choice: %s' % self.choice_keys_str()

    def choice_keys_str(self):
        result = ''
        for option in self.options:
            if isinstance(option, list):
                result += ' (%s) ' % ','.join(item.tag for item in option)
            else:
                result += ' %s ' % option.tag
        return '(%s)' % ' | '.join(result.strip().split()).replace(',', ', ')

    def _flat_options_dict(self):
        flattened = []
        assert_msg = "Choice options may only be of type ElementSchema or " \
                     "list of ElementSchema"
        for option in self.options:
            if isinstance(option, list):
                for item in option:
                    assert isinstance(item, ElementSchema), assert_msg
                flattened.extend(option)
            else:
                assert isinstance(option, ElementSchema), assert_msg
                flattened.append(option)
        return {option.tag: option for option in flattened}

    def choice_to_key_sets(self, required):
        key_sets = [set([]) for option in self.options]
        for index, option in enumerate(self.options):
            if isinstance(option, ElementSchema):
                if (option.minOccurs > 0) == required:
                    key_sets[index].add(option.tag)
            elif isinstance(option, list):
                [key_sets[index].add(field.tag) for field in option
                 if (field.minOccurs > 0) == required]
        return key_sets

    def match_choice_keys(self, value_key_set):
        no_match_msg = "Could not match keys: %s with: choices: %s" % (
            ', '.join(value_key_set), self.choice_keys_str())
        if value_key_set == set([]) and not self.required:
            return []
        max_key_sets = [self.required_keys_sets[i] | self.optional_keys_sets[i]
                        for i in range(len(self.options))]
        min_key_matches = [value_key_set >= min_keys
                           for min_keys in self.required_keys_sets]
        max_key_matches = [value_key_set <= max_keys
                           for max_keys in max_key_sets]
        if not any(min_key_matches):
            utils.error(logger, no_match_msg)
        if not any(max_key_matches):
            utils.error(logger, no_match_msg)
        if any(min_key_matches) and any(max_key_matches):
            matches = [i for i in range(len(self.options))
                       if min_key_matches[i] and max_key_matches[i]]
            if isinstance(self.options[matches[0]], ElementSchema):
                matched_fields = [self.options[matches[0]]]
            else:
                matched_fields = [field
                                  for field in self.options[matches[0]]
                                  if field.tag in value_key_set]
            msg = "Matched keys: %s with option: %d" % \
                  (', '.join(value_key_set), matches[0])
            utils.debug(logger, msg)
            return matched_fields
        return [self._flat_options[tag] for tag in value_key_set
                if tag in self._flat_options]


class SequenceSchema(Validator):
    sequence = []
    attributes = None
    initial = None
    tag = ''
    default = None
    index = 0
    not_empty = True
    messages = dict(
        missingField='Required field %(field)s is missing.',
        validatingInfo='Validating instance',
        emptyChild='The field: %s should not be empty!',
    )

    def check_key_order(self, value_tags, sequence, parent_path):
        validator_keys = [field.tag for field in sequence]
        if value_tags != validator_keys:
            utils.warning(logger, "The order of the keys in %s ( %s ) does "
                                  "not match the expected order { %s )." %
                                  (parent_path,
                                   ', '.join(value_tags),
                                   ', '.join(validator_keys)))

    def match_sequence(self, value_tags, parent_path):
        result_sequence = []
        covered_tags_set = set([])
        failed = False
        for field in self.sequence:
            if isinstance(field, ElementSchema):
                if field.tag in value_tags:
                    result_sequence.append(field)
                elif field.minOccurs > 0:
                    msg = "Missing required key: %s" % field.tag
                    utils.error(logger, msg)
                    failed = True
                covered_tags_set.add(field.tag)
            elif isinstance(field, Choice):
                choice_keys_sey = set(value_tags) & field.all_keys_set
                cs = field.match_choice_keys(choice_keys_sey)
                covered_tags_set = covered_tags_set | field.all_keys_set
                if cs:
                    result_sequence.extend(cs)
        extra_tags = set(value_tags) - covered_tags_set
        if extra_tags:
            msg = "Could not match tag(s): %s" % ', '.join(extra_tags)
            utils.error(logger, msg)
        elif not failed:
            self.check_key_order(value_tags, result_sequence, parent_path)
        return result_sequence

    def to_python(self, elements_list, **kwargs):
        if elements_list is None and not self.not_empty:
            pass
        else:
            if not isinstance(elements_list, list):
                raise ValidationException('Expected child elements.', elements_list)
            if self.initial:
                self.initial.to_python(None, **kwargs)
            for element in elements_list:
                if not isinstance(element, Element):
                    raise ValidationException('All values must be of type Element.',
                                              elements_list)
            el_dict = OrderedDict()
            for element in elements_list:
                if element.tag in el_dict:
                    if isinstance(el_dict[element.tag], list):
                        el_dict[element.tag].append(element)
                    else:
                        el_dict[element.tag] = [el_dict[element.tag],
                                                element]
                else:
                    el_dict[element.tag] = element
            tag = '(%s)' % el_dict['tag'].value if 'tag' in el_dict else ''
            parent_path = '/'.join(elements_list[0].path.split('/')[:-1])
            msg = 'Validating: %s for element <%s%s> with keys: %s' % (
                parent_path, self.tag, tag, ', '.join(el_dict.keys()))
            utils.debug(logger, msg)
            sequence = self.match_sequence(el_dict.keys(), parent_path)
            result = []
            if sequence:
                for element_schema in sequence:
                    field_element = el_dict[element_schema.tag]
                    if isinstance(field_element, list):
                        validated_elements = [element_schema.to_python(item, **kwargs)
                                              for item in field_element]
                        result.extend(validated_elements)
                    else:
                        validated_element = element_schema.to_python(field_element, **kwargs)
                        result.append(validated_element)
            return result

    def build(self, *args, **kwargs):
        return super(SequenceSchema, self).build(*args, **kwargs)


