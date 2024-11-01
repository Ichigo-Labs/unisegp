"""Unicode word boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

from enum import Enum
from typing import Iterator, Optional

from uniseg.breaking import (Breakable, Breakables, Run, TailorFunc,
                             boundaries, break_units)
from uniseg.codepoint import code_point
from uniseg.db import extended_pictographic
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

AHLetterTuple = (WB.ALETTER, WB.HEBREW_LETTER)
MidNumLetQTuple = (WB.MIDNUMLET, WB.SINGLE_QUOTE)


def word_break(c: str, index: int = 0, /) -> WordBreak:
    R"""Return the Word_Break property of `c`

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


def word_breakables(s: str, /) -> Breakables:
    R"""Iterate word breaking opportunities for every position of `s`

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
        return iter([])

    run = Run(s, word_break)
    while run.walk():
        # WB3
        if run.prev == WB.CR and run.curr == WB.LF:
            run.do_not_break_here()
        # WB3a
        elif run.prev in (WB.NEWLINE, WB.CR, WB.LF):
            run.break_here()
        # WB3b
        elif run.curr in (WB.NEWLINE, WB.CR, WB.LF):
            run.break_here()
        # WB3c
        elif run.prev == WB.ZWJ and run.cc and extended_pictographic(run.cc):
            run.do_not_break_here()
        # WB3d
        elif run.prev == run.curr == WB.WSEGSPACE:
            run.do_not_break_here()
        # WB4
        elif run.curr in (WB.FORMAT, WB.EXTEND, WB.ZWJ):
            run.do_not_break_here()
    # WB4
    run.skip((WB.EXTEND, WB.FORMAT, WB.ZWJ))
    run.head()
    while run.walk():
        # WB5
        if run.prev in AHLetterTuple and run.curr in AHLetterTuple:
            run.do_not_break_here()
        # WB6
        elif (
            run.prev in AHLetterTuple
            and run.curr in (WB.MIDLETTER,) + MidNumLetQTuple
            and run.next in AHLetterTuple
        ):
            run.do_not_break_here()
        # WB7
        elif (
            run.value(-2) in AHLetterTuple
            and run.prev in (WB.MIDLETTER,) + MidNumLetQTuple
            and run.curr in AHLetterTuple
        ):
            run.do_not_break_here()
        # WB7a
        elif run.prev == WB.HEBREW_LETTER and run.curr == WB.SINGLE_QUOTE:
            run.do_not_break_here()
        # WB7b
        elif (
            run.prev == WB.HEBREW_LETTER
            and run.curr == WB.DOUBLE_QUOTE
            and run.next == WB.HEBREW_LETTER
        ):
            run.do_not_break_here()
        # WB7c
        elif (
            run.value(-2) == WB.HEBREW_LETTER
            and run.prev == WB.DOUBLE_QUOTE
            and run.curr == WB.HEBREW_LETTER
        ):
            run.do_not_break_here()
        # WB8
        elif run.prev == run.curr == WB.NUMERIC:
            run.do_not_break_here()
        # WB9
        elif run.prev in AHLetterTuple and run.curr == WB.NUMERIC:
            run.do_not_break_here()
        # WB10
        elif run.prev == WB.NUMERIC and run.curr in AHLetterTuple:
            run.do_not_break_here()
        # WB11
        elif (
            run.value(-2) == WB.NUMERIC
            and run.prev in (WB.MIDNUM,) + MidNumLetQTuple
            and run.curr == WB.NUMERIC
        ):
            run.do_not_break_here()
        # WB12
        elif (
            run.prev == WB.NUMERIC
            and run.curr in (WB.MIDNUM,) + MidNumLetQTuple
            and run.next == WB.NUMERIC
        ):
            run.do_not_break_here()
        # WB13
        elif run.prev == run.curr == WB.KATAKANA:
            run.do_not_break_here()
        # WB13a
        elif (
            run.prev in AHLetterTuple + (WB.NUMERIC, WB.KATAKANA, WB.EXTENDNUMLET)
            and run.curr == WB.EXTENDNUMLET
        ):
            run.do_not_break_here()
        # WB13b
        elif (
            run.prev == WB.EXTENDNUMLET
            and run.curr in AHLetterTuple + (WB.NUMERIC, WB.KATAKANA)
        ):
            run.do_not_break_here()
    run.head()
    # WB15, WB16
    while 1:
        while run.curr != WB.REGIONAL_INDICATOR:
            if not run.walk():
                break
        if not run.walk():
            break
        while run.prev == run.curr == WB.REGIONAL_INDICATOR:
            run.do_not_break_here()
            if not run.walk():
                break
            if not run.walk():
                break
    # WB999
    run.set_default(Breakable.Break)
    return run.literal_breakables()


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
