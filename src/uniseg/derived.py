"""Unicode derived properties.

`UAX #44: Unicode Character Database (16.0.0)
<https://www.unicode.org/reports/tr44/tr44-34.html>`_
"""

from uniseg import UnicodeProperty
from uniseg.db import get_column_index, get_value

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
