"""Unicode Extended_Pictographic property.

UAX #29: Unicode Text Segmentation (Unicode 15.0.0)
https://www.unicode.org/reports/tr29/tr29-41.html
"""

import enum
from typing import Callable, Iterator, Optional

from uniseg.breaking import boundaries, break_units, Breakables, TailorFunc
from uniseg.codepoint import code_point, code_points
from uniseg.db import extended_pictographic as _extended_pictographic


__all__ = [
    'ExtendedPictographic',
    'extended_pictographic',
]


@enum.unique
class ExtendedPictographic(enum.Enum):
    """Extended_Pictographic property values.

    Listed in <http://www.unicode.org/Public/15.0.0/ucd/emoji/emoji-data.txt>.

    >>> bool(ExtendedPictographic.NO)
    False
    >>> bool(ExtendedPictographic.YES)
    True
    """
    NO = False
    YES = True

    def __bool__(self):
        return bool(self.value)


def extended_pictographic(c: str, index: int = 0, /) -> ExtendedPictographic:

    """Return the Extended_Pictographic property of `c`

    `c` must be a single Unicode code point string.

    >>> extended_pictographic('a')
    <ExtendedPictographic.NO: False>
    >>> extended_pictographic('©️')
    <ExtendedPictographic.YES: True>

    If `index` is specified, this function consider `c` as a unicode
    string and return its property of the code point at c[index].

    >>> extended_pictographic('a©', 1)
    <ExtendedPictographic.YES: True>
    """

    name = _extended_pictographic(code_point(c, index))
    return ExtendedPictographic[name.upper()]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
