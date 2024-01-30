"""Unicode Indic Conjunct Break property.

UAX #29: Unicode Text Segmentation (Unicode 15.1.0)
https://www.unicode.org/reports/tr29/tr29-43.html
"""

import enum
from typing import Callable, Iterator, Optional

from uniseg.breaking import boundaries, break_units, Breakables, TailorFunc
from uniseg.codepoint import code_point, code_points
from uniseg.db import indic_conjunct_break as _indic_conjunct_break

__all__ = [
    'IndicConjunctBreakProperty',
]


@enum.unique
class IndicConjunctBreakProperty(enum.Enum):
    """Indic_Conjunct_Break property values in UAX #29.

    Listed in <http://www.unicode.org/Public/15.1.0/ucd/DerivecCoreProperties.txt>.
    """
    None_ = 0
    Linker = 1
    Consonant = 2
    Extend = 3


def indic_conjunct_break(c: str, index: int = 0, /) -> Optional[IndicConjunctBreakProperty]:

    r"""Return the Indic_Conjunct_Break property of `c`

    `c` must be a single Unicode code point string.

    >>> indic_conjunct_break('a')
    >>> indic_conjunct_break('\u094d')
    <IndicConjunctBreakProperty.Linker: 1>
    >>> indic_conjunct_break('\u0300').name
    'Extend'

    If `index` is specified, this function consider `c` as a unicode
    string and return Grapheme_Cluster_Break property of the code
    point at c[index].

    >>> indic_conjunct_break('a\u0915', 1).name
    'Consonant'
    """

    name = _indic_conjunct_break(code_point(c, index))
    incb = IndicConjunctBreakProperty[name]
    return incb if incb != IndicConjunctBreakProperty.None_ else None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
