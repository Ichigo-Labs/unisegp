"""Unicode derived properties.

`UAX #44: Unicode Character Database (16.0.0)
<https://www.unicode.org/reports/tr44/tr44-34.html>`_
"""

from uniseg import UnicodeProperty
from uniseg.db import get_column_index, get_value

__all__ = [
    'IndicConjunctBreak',
    'InCB',
    'math',
    'alphabetic',
    'lowercase',
    'uppercase',
    'cased',
    'case_ignorable',
    'changes_when_lowercased',
    'changes_when_uppercased',
    'changes_when_titlecased',
    'changes_when_casefolded',
    'changes_when_casemapped',
    'id_start',
    'id_continue',
    'xid_start',
    'xid_continue',
    'default_ignorable_code_point',
    'grapheme_extend',
    'grapheme_base',
    'indic_conjunct_break',
]


INDEX_MATH = get_column_index('Math')
INDEX_ALPHABETIC = get_column_index('Alphabetic')
INDEX_LOWERCASE = get_column_index('Lowercase')
INDEX_UPPERCASE = get_column_index('Uppercase')
INDEX_CASED = get_column_index('Cased')
INDEX_CASE_IGNORABLE = get_column_index('Case_Ignorable')
INDEX_CHANGES_WHEN_LOWERCASED = get_column_index('Changes_When_Lowercased')
INDEX_CHANGES_WHEN_UPPERCASED = get_column_index('Changes_When_Uppercased')
INDEX_CHANGES_WHEN_TITLECASED = get_column_index('Changes_When_Titlecased')
INDEX_CHANGES_WHEN_CASEFOLDED = get_column_index('Changes_When_Casefolded')
INDEX_CHANGES_WHEN_CASEMAPPED = get_column_index('Changes_When_Casemapped')
INDEX_ID_START = get_column_index('ID_Start')
INDEX_ID_CONTINUE = get_column_index('ID_Continue')
INDEX_XID_START = get_column_index('XID_Start')
INDEX_XID_CONTINUE = get_column_index('XID_Continue')
INDEX_DEFAULT_IGNORABLE_CODE_POINT = get_column_index(
    'Default_Ignorable_Code_Point')
INDEX_GRAPHEME_EXTEND = get_column_index('Grapheme_Extend')
INDEX_GRAPHEME_BASE = get_column_index('Grapheme_Base')
INDEX_INDIC_CONJUNCT_BREAK = get_column_index('InCB')


class IndicConjunctBreak(UnicodeProperty):
    """Derived Property: Indic_Conjunct_Break."""
    None_ = 'None'
    """Indic_Conjunct_Break=None"""
    Linker = 'Linker'
    """Indic_Conjunct_Break=Linker"""
    Consonant = 'Consonant'
    """Indic_Conjunct_Break=Consonant"""
    Extend = 'Extend'
    """Indic_Conjunct_Break=Extend"""


InCB = IndicConjunctBreak


def math(ch: str, /) -> bool:
    """Return Math boolean derived Unicode property value for `ch`.

    >>> math('A')
    False
    >>> math('+')
    True
    """
    return bool(get_value(ord(ch), INDEX_MATH))


def alphabetic(ch: str, /) -> bool:
    """Return Alphabetic boolean derived Unicode property value for `ch`.

    >>> alphabetic('A')
    True
    >>> alphabetic('1')
    False
    """
    return bool(get_value(ord(ch), INDEX_ALPHABETIC))


def lowercase(ch: str, /) -> bool:
    """Return Lowercase boolean derived Unicode property value for `ch`.

    >>> lowercase('A')
    False
    >>> lowercase('a')
    True
    """
    return bool(get_value(ord(ch), INDEX_LOWERCASE))


def uppercase(ch: str, /) -> bool:
    """Return Uppercase boolean derived Unicode property value for `ch`.

    >>> uppercase('A')
    True
    >>> uppercase('a')
    False
    """
    return bool(get_value(ord(ch), INDEX_UPPERCASE))


def cased(ch: str, /) -> bool:
    """Return Cased boolean derived Unicode property value for `ch`.

    >>> cased('A')
    True
    >>> cased('a')
    True
    >>> cased('*')
    False
    """
    return bool(get_value(ord(ch), INDEX_CASED))


def case_ignorable(ch: str, /) -> bool:
    """Return Case_Ignorable boolean derived Unicode property value for `ch`.

    >>> case_ignorable('A')
    False
    >>> case_ignorable('.')
    True
    """
    return bool(get_value(ord(ch), INDEX_CASE_IGNORABLE))


def changes_when_lowercased(ch: str, /) -> bool:
    """Return Changes_When_Lowercased boolean derived Unicode property value
    for `ch`.

    >>> changes_when_lowercased('A')
    True
    >>> changes_when_lowercased('a')
    False
    """
    return bool(get_value(ord(ch), INDEX_CHANGES_WHEN_LOWERCASED))


def changes_when_uppercased(ch: str, /) -> bool:
    """Return Changes_When_Uppercased boolean derived Unicode property value
    for `ch`.

    >>> changes_when_uppercased('A')
    False
    >>> changes_when_uppercased('a')
    True
    """
    return bool(get_value(ord(ch), INDEX_CHANGES_WHEN_UPPERCASED))


def changes_when_titlecased(ch: str, /) -> bool:
    """Return Changes_When_Titlecased boolean derived Unicode property value
    for `ch`.

    >>> changes_when_titlecased('A')
    False
    >>> changes_when_titlecased('a')
    True
    """
    return bool(get_value(ord(ch), INDEX_CHANGES_WHEN_TITLECASED))


def changes_when_casefolded(ch: str, /) -> bool:
    """Return Changes_When_Casefolded boolean derived Unicode property value
    for `ch`.

    >>> changes_when_casefolded('A')
    True
    >>> changes_when_casefolded('a')
    False
    """
    return bool(get_value(ord(ch), INDEX_CHANGES_WHEN_CASEFOLDED))


def changes_when_casemapped(ch: str, /) -> bool:
    """Return Changes_When_Casemapped boolean derived Unicode property value
    for `ch`.

    >>> changes_when_casemapped('A')
    True
    >>> changes_when_casemapped('a')
    True
    >>> changes_when_casemapped('1')
    False
    """
    return bool(get_value(ord(ch), INDEX_CHANGES_WHEN_CASEMAPPED))


def id_start(ch: str, /) -> bool:
    """Return ID_Start boolean derived Unicode property value for `ch`.

    >>> id_start('A')
    True
    >>> id_start('a')
    True
    >>> id_start('1')
    False
    """
    return bool(get_value(ord(ch), INDEX_ID_START))


def id_continue(ch: str, /) -> bool:
    """Return ID_Continue boolean derived Unicode property value for `ch`.

    >>> id_continue('A')
    True
    >>> id_continue('a')
    True
    >>> id_continue('1')
    True
    >>> id_continue('.')
    False
    """
    return bool(get_value(ord(ch), INDEX_ID_CONTINUE))


def xid_start(ch: str, /) -> bool:
    """Return XID_Start boolean derived Unicode property value for `ch`.

    >>> xid_start('A')
    True
    >>> xid_start('a')
    True
    >>> xid_start('1')
    False
    """
    return bool(get_value(ord(ch), INDEX_XID_START))


def xid_continue(ch: str, /) -> bool:
    """Return XID_Continue boolean derived Unicode property value for `ch`.

    >>> xid_continue('A')
    True
    >>> xid_continue('a')
    True
    >>> xid_continue('1')
    True
    >>> xid_continue('.')
    False
    """
    return bool(get_value(ord(ch), INDEX_XID_CONTINUE))


def default_ignorable_code_point(ch: str, /) -> bool:
    """Return Default_Ignorable_Code_Point boolean derived Unicode property
    value for `ch`.

    >>> default_ignorable_code_point('A')
    False
    >>> default_ignorable_code_point('\u00ad')
    True
    """
    return bool(get_value(ord(ch), INDEX_DEFAULT_IGNORABLE_CODE_POINT))


def grapheme_extend(ch: str, /) -> bool:
    """Return Grapheme_Extend boolean derived Unicode property value for `ch`.

    >>> grapheme_extend('A')
    False
    >>> grapheme_extend('\u0300')
    True
    """
    return bool(get_value(ord(ch), INDEX_GRAPHEME_EXTEND))


def grapheme_base(ch: str, /) -> bool:
    """Return Grapheme_Base boolean derived Unicode property value for `ch`.

    >>> grapheme_base('A')
    True
    >>> grapheme_extend('\u0300')
    True
    """
    return bool(get_value(ord(ch), INDEX_GRAPHEME_BASE))


def indic_conjunct_break(ch: str, /) -> IndicConjunctBreak:
    """Retrun Indic_Conjunct_Break derived property for `ch`.

    >>> indic_conjunct_break('A')
    IndicConjunctBreak.None_
    >>> indic_conjunct_break('\u094d')
    IndicConjunctBreak.Linker
    """
    return IndicConjunctBreak[
        get_value(ord(ch), INDEX_INDIC_CONJUNCT_BREAK) or 'None_'
    ]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
