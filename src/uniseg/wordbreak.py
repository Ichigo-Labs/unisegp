"""Unicode word boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

from enum import Enum
from typing import Iterator, Optional, Tuple

from uniseg.breaking import Breakables, TailorFunc, boundaries, break_units
from uniseg.codepoint import code_point, code_points
from uniseg.db import word_break as _word_break

__all__ = [
    'WordBreak',
    'WB',
    'word_break',
    'word_breakables',
    'word_boundaries',
    'words',
]


class WordBreak(Enum):
    """Word_Break property values."""
    OTHER = 'Other'
    CR = 'CR'
    LF = 'LF'
    NEWLINE = 'Newline'
    EXTEND = 'Extend'
    ZWJ = 'ZWJ'
    REGIONAL_INDICATOR = 'Regional_Indicator'
    FORMAT = 'Format'
    KATAKANA = 'Katakana'
    HEBREW_LETTER = 'Hebrew_Letter'
    ALETTER = 'ALetter'
    SINGLE_QUOTE = 'Single_Quote'
    DOUBLE_QUOTE = 'Double_Quote'
    MIDNUMLET = 'MidNumLet'
    MIDLETTER = 'MidLetter'
    MIDNUM = 'MidNum'
    NUMERIC = 'Numeric'
    EXTENDNUMLET = 'ExtendNumLet'
    WSEGSPACE = 'WSegSpace'


# type alias for `WordBreak`
WB = WordBreak

AHLetterGroup = (WB.ALETTER, WB.HEBREW_LETTER)
MidNumLetQGroup = (WB.MIDNUMLET, WB.SINGLE_QUOTE)


def word_break(c: str, index: int = 0, /) -> WordBreak:
    r"""Return the Word_Break property of `c`

    `c` must be a single Unicode code point string.

    >>> word_break('\x0d')
    <WordBreak.CR: 'CR'>
    >>> word_break('\x0b')
    <WordBreak.NEWLINE: 'Newline'>
    >>> word_break('\u30a2')
    <WordBreak.KATAKANA: 'Katakana'>

    If `index` is specified, this function consider `c` as a unicode
    string and return Word_Break property of the code point at
    c[index].

    >>> word_break('A\u30a2', 1)
    <WordBreak.KATAKANA: 'Katakana'>
    """

    return WordBreak[_word_break(code_point(c, index)).upper()]


def _preprocess_boundaries(s: str, /) -> Iterator[Tuple[int, WordBreak]]:
    r"""(internal) Preprocess WB4; X (Extend | Format | ZWJ)* -> X

    >>> list(_preprocess_boundaries('\r\n'))
    [(0, <WordBreak.CR: 'CR'>), (1, <WordBreak.LF: 'LF'>)]
    >>> list(_preprocess_boundaries('A\u0308A'))
    [(0, <WordBreak.ALETTER: 'ALetter'>), (2, <WordBreak.ALETTER: 'ALetter'>)]
    >>> list(_preprocess_boundaries('\n\u2060'))
    [(0, <WordBreak.LF: 'LF'>), (1, <WordBreak.FORMAT: 'Format'>)]
    >>> list(_preprocess_boundaries('\x01\u0308\x01'))
    [(0, <WordBreak.OTHER: 'Other'>), (2, <WordBreak.OTHER: 'Other'>)]
    """

    prev_prop = None
    i = 0
    for c in code_points(s):
        prop = word_break(c)
        if prop in (WB.NEWLINE, WB.CR, WB.LF):
            yield (i, prop)
            prev_prop = None
        elif prop in (WB.EXTEND, WB.FORMAT, WB.ZWJ):
            if prev_prop is None:
                yield (i, prop)
                prev_prop = prop
        else:
            yield (i, prop)
            prev_prop = prop
        i += len(c)


def word_breakables(s: str, /) -> Breakables:
    r"""Iterate word breaking opportunities for every position of `s`

    1 for "break" and 0 for "do not break".  The length of iteration
    will be the same as ``len(s)``.

    >>> list(word_breakables('ABC'))
    [1, 0, 0]
    >>> list(word_breakables('Hello, world.'))
    [1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1]
    >>> list(word_breakables('\x01\u0308\x01'))
    [1, 0, 1]
    """

    if not s:
        return

    primitive_boundaries = list(_preprocess_boundaries(s))
    prev_prev_wb = None
    prev_wb = None
    for i, (pos, wb) in enumerate(primitive_boundaries):
        next_pos, next_wb = (primitive_boundaries[i+1]
                             if i < len(primitive_boundaries)-1 else (len(s), None))
        # print pos, prev_wb, wb
        if (prev_wb in (WB.NEWLINE, WB.CR, WB.LF)
                or wb in (WB.NEWLINE, WB.CR, WB.LF)):
            do_break = not (prev_wb == WB.CR and wb == WB.LF)
        # WB5
        elif prev_wb in AHLetterGroup and wb in AHLetterGroup:
            do_break = False
        # WB6
        elif prev_wb == next_wb == WB.ALETTER and wb in (WB.MIDLETTER, WB.MIDNUMLET):
            do_break = False
        # WB7
        elif (prev_prev_wb == wb == WB.ALETTER and prev_wb in (WB.MIDLETTER, WB.MIDNUMLET)):
            do_break = False
        # WB8
        elif prev_wb == wb == WB.NUMERIC:
            do_break = False
        # WB9
        elif prev_wb == WB.ALETTER and wb == WB.NUMERIC:
            do_break = False
        # WB10
        elif (
            (prev_wb == wb == WB.NUMERIC)
            or (prev_wb in AHLetterGroup and wb == WB.NUMERIC)
            or (prev_wb == WB.NUMERIC and wb in AHLetterGroup)
        ):
            do_break = False
        # WB11
        elif prev_prev_wb == wb == WB.NUMERIC and prev_wb in (WB.MIDNUM, WB.MIDNUMLET):
            do_break = False
        # WB12
        elif prev_wb == next_wb == WB.NUMERIC and wb in (WB.MIDNUM, WB.MIDNUMLET):
            do_break = False
        # WB13
        # WB13a WB13b
        elif (prev_wb == wb == WB.KATAKANA
              or (prev_wb in (WB.ALETTER, WB.NUMERIC, WB.KATAKANA, WB.EXTENDNUMLET)
                  and wb == WB.EXTENDNUMLET)
              or (prev_wb == WB.EXTENDNUMLET
                  and wb in (WB.ALETTER, WB.NUMERIC, WB.KATAKANA))):
            do_break = False
        # WB13c
        elif prev_wb == wb == WB.REGIONAL_INDICATOR:
            do_break = False
        # WB14
        else:
            do_break = True
        for j in range(next_pos-pos):
            yield 1 if (j == 0 and do_break) else 0
        prev_prev_wb = prev_wb
        prev_wb = wb


def word_boundaries(s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[int]:
    """Iterate indices of the word boundaries of `s`

    This function yields indices from the first boundary position (> 0)
    to the end of the string (== len(s)).
    """

    breakables = word_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def words(s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[str]:
    """Iterate *user-perceived* words of `s`

    These examples bellow is from
    http://www.unicode.org/reports/tr29/tr29-15.html#Word_Boundaries

    >>> s = 'The quick (“brown”) fox can’t jump 32.3 feet, right?'
    >>> print('|'.join(words(s)))
    The| |quick| |(|“|brown|”|)| |fox| |can’t| |jump| |32.3| |feet|,| |right|?
    >>> list(words(''))
    []
    """

    breakables = word_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
