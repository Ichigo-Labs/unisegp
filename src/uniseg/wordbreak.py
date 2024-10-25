"""Unicode word boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

from collections.abc import Sequence
from enum import Enum
from typing import Iterator, Literal, Optional

from uniseg.breaking import Breakables, TailorFunc, boundaries, break_units
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


class Runner(object):

    def __init__(self, s: str):
        self._text = s
        self._values = [word_break(c) for c in s]
        self._skip = tuple[str, ...]()
        self._breakables: list[Literal[0, 1]] = [1 for __ in s]
        self._i = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def values(self) -> list[WordBreak]:
        return self._values

    @property
    def breakables(self) -> list[Literal[0, 1]]:
        return self._breakables

    @property
    def position(self) -> int:
        return self._i

    @property
    def curr(self) -> Optional[WordBreak]:
        return self.value()

    @property
    def prev(self) -> Optional[WordBreak]:
        return self.value(-1)

    @property
    def next(self) -> Optional[WordBreak]:
        return self.value(1)

    @property
    def chr(self) -> str:
        return self._text[self._i]

    def value(self, offset: int = 0) -> Optional[WordBreak]:
        i = self._i
        if offset == 0:
            return self._values[i] if 0 <= i < len(self._text) else None
        vec = offset // abs(offset)
        for __ in range(abs(offset)):
            i += vec
            while 0 <= i < len(self._text) and self._values[i] in self._skip:
                i += vec
        if 0 <= i < len(self._text):
            return self._values[i]
        return None

    def walk(self) -> bool:
        self._i += 1
        while self._i < len(self._text) and self._values[self._i] in self._skip:
            self._i += 1
        return self._i < len(self._text)

    def head(self) -> None:
        self._i = 0

    def skip(self, values: Sequence[WordBreak]) -> None:
        self._skip = tuple(values)

    def break_here(self) -> None:
        self._breakables[self._i] = 1

    def do_not_break_here(self) -> None:
        self._breakables[self._i] = 0

    def does_break_here(self) -> bool:
        return bool(self._breakables[self._i])


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
        return iter([])

    run = Runner(s)
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
        elif run.prev == WB.ZWJ and extended_pictographic(run.chr):
            run.do_not_break_here()
        # WB3d
        elif run.prev == run.curr == WB.WSEGSPACE:
            run.do_not_break_here()
        # WB4
        elif run.curr in (WB.FORMAT, WB.EXTEND, WB.ZWJ):
            run.do_not_break_here()
    # WB4
    run.head()
    run.skip((WB.EXTEND, WB.FORMAT, WB.ZWJ))
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
        elif (
            run.prev == WB.HEBREW_LETTER
            and run.curr == WB.SINGLE_QUOTE
        ):
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
            run.prev in AHLetterTuple +
                (WB.NUMERIC, WB.KATAKANA, WB.EXTENDNUMLET)
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
    # WB15
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

    return iter(run.breakables)


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
