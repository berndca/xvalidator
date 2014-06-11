"""
xvalidator Validation Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



:copyright: (c) 2014 by Bernd Meyer.
:license: BSD 3-Clause, see LICENSE for more details.

"""

__title__ = 'xvalidator'
__version__ = '0.1.0'
__build__ = 0x000042
__author__ = 'Bernd Meyer'
__license__ = 'BSD 3-Clause'
__copyright__ = 'Copyright 2014 Bernd Meyer'

from .constraints import Stores,InitKeyStore, InitUniqueStore, \
    ID, IDREF, KeyName, UniqueName
from .element import Element, create_element, Document, create_document
from .schemas import ElementSchema, SequenceSchema
from .validators import StringValidator, Token, Name, NCName, Language, \
    NMTOKEN, IntegerValidator, NonNegativeInteger, PositiveInteger, \
    NegativeInteger, FloatValidator, NonNegativeFloat, BooleanValidator, \
    EnumValidator