from __future__ import unicode_literals
import logging

import nose
from nose.tools import raises

from xvalidator import utils
from xvalidator.element import Element


__author__ = 'bernd'

logger = logging.getLogger(__name__)


def test_common_equality_mixin_not_equal_pass():
    element1 = Element('tag1')
    element2 = Element('tag2')
    assert element1 != element2


def test_warning_pass():
    utils.reset_message_counters()
    utils.warning(logger, 'test_warning_state_None')
    nose.tools.eq_(utils.warning_count, 1)


def test_warning_max_warnings_0_pass():
    utils.reset_message_counters()
    utils.warning(logger, 'test_warning_maxWarnings_0')
    nose.tools.eq_(utils.warning_count, 1)


# def test_warning_max_warnings_1_pass():
#     utils.reset_message_counters()
#     utils.warning.set_max_value(1)
#     utils.warning(logger, 'test_warning_maxWarnings_1')
#     utils.warning(logger, 'test_warning_maxWarnings_1')
#     nose.tools.eq_(utils.warning_count, 2)


def test_error_pass():
    utils.reset_message_counters()
    utils.error(logger, 'test_error_state_None')
    nose.tools.eq_(utils.error_count, 1)


# def test_error_max_errors_0_pass():
#     utils.reset_message_counters()
#     utils.error.set_max_value(0)
#     utils.error(logger, 'test_error_maxErrors_0')
#     nose.tools.eq_(utils.error_count, 1)
#
#
# def test_error_max_errors_1_pass():
#     utils.reset_message_counters()
#     utils.error.set_max_value(1)
#     utils.error(logger, 'test_error_maxErrors_1')
#     nose.tools.eq_(utils.error_count, 1)


def test_message_count_info_pass():
    """Noop
    """
    utils.reset_message_counters()
    utils.message_count_info(logger, 'test_message_count_info_state_None')


def test_message_count_info_no_errors():
    utils.reset_message_counters()
    utils.message_count_info(logger, 'test_message_count_info_no_errors')


def test_message_count_info_errors_no_abort():
    utils.reset_message_counters()
    utils.error(logger, 'test_message_count_info_errors_no_abort')
    utils.message_count_info(logger, 'test_message_count_info_errors_no_abort',
                             abort_on_errors=False)


@raises(SystemExit)
def test_message_count_info_errors_abort():
    utils.reset_message_counters()
    utils.error(logger, 'test_message_count_info_errors_abort')
    utils.message_count_info(logger, 'test_message_count_info_errors_abort',
                             abort_on_errors=True)


