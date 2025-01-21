"""Unicode word boundaries.

`UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
<https://www.unicode.org/reports/tr29/tr29-45.html>`_
"""

from typing import Iterator, Optional

from uniseg import Unicode_Property
from uniseg.breaking import (Breakable, Breakables, Run, TailorBreakables, boundaries,
                             break_units)
from uniseg.db import get_handle, get_value
from uniseg.emoji import extended_pictographic

__all__ = [
    'Word_Break',
    'WB',
    'word_break',
    'word_breakables',
    'word_boundaries',
    'words',
]


H_WORD_BREAK = get_handle('Word_Break')


class Word_Break(Unicode_Property):
    """Word_Break property values."""
    Other = 'Other'
    """Word_Break property value Other"""
    CR = 'CR'
    """Word_Break property value CR"""
    LF = 'LF'
    """Word_Break property value LF"""
    Newline = 'Newline'
    """Word_Break property value Newline"""
    Extend = 'Extend'
    """Word_Break property value Extend"""
    ZWJ = 'ZWJ'
    """Word_Break property value ZWJ"""
    Regional_Indicator = 'Regional_Indicator'
    """Word_Break property value Regional_Indicator"""
    Format = 'Format'
    """Word_Break property value Format"""
    Katakana = 'Katakana'
    """Word_Break property value Katakana"""
    Hebrew_Letter = 'Hebrew_Letter'
    """Word_Break property value Hebrew_Letter"""
    ALetter = 'ALetter'
    """Word_Break property value ALetter"""
    Single_Quote = 'Single_Quote'
    """Word_Break property value Single_Quote"""
    Double_Quote = 'Double_Quote'
    """Word_Break property value Double_Quote"""
    MidNumLet = 'MidNumLet'
    """Word_Break property value MidNumLet"""
    MidLetter = 'MidLetter'
    """Word_Break property value MidLetter"""
    MidNum = 'MidNum'
    """Word_Break property value MidNum"""
    Numeric = 'Numeric'
    """Word_Break property value Numeric"""
    ExtendNumLet = 'ExtendNumLet'
    """Word_Break property value ExtendNumLet"""
    WSegSpace = 'WSegSpace'
    """Word_Break property value WSegSpace"""


# type alias for `WordBreak`
WB = Word_Break

AHLetterTuple = (WB.ALetter, WB.Hebrew_Letter)
MidNumLetQTuple = (WB.MidNumLet, WB.Single_Quote)


def word_break(c: str, /) -> Word_Break:
    R"""Return the Word_Break property of `c`

    `c` must be a single Unicode code point string.

    >>> word_break('\r')
    Word_Break.CR
    >>> word_break('\x0b')
    Word_Break.Newline
    >>> word_break('ア')
    Word_Break.Katakana
    """
    return Word_Break[get_value(H_WORD_BREAK, ord(c)) or 'Other']


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
        elif run.prev in (WB.Newline, WB.CR, WB.LF):
            run.break_here()
        # WB3b
        elif run.curr in (WB.Newline, WB.CR, WB.LF):
            run.break_here()
        # WB3c
        elif run.prev == WB.ZWJ and run.cc and extended_pictographic(run.cc):
            run.do_not_break_here()
        # WB3d
        elif run.prev == run.curr == WB.WSegSpace:
            run.do_not_break_here()
        # WB4
        elif run.curr in (WB.Format, WB.Extend, WB.ZWJ):
            run.do_not_break_here()
    # WB4
    run.set_skip_table(x not in (WB.Extend, WB.Format, WB.ZWJ)
                       for x in run.attributes())
    run.head()
    while run.walk():
        # WB5
        if run.prev in AHLetterTuple and run.curr in AHLetterTuple:
            run.do_not_break_here()
        # WB6
        elif (
            run.prev in AHLetterTuple
            and run.curr in (WB.MidLetter,) + MidNumLetQTuple
            and run.next in AHLetterTuple
        ):
            run.do_not_break_here()
        # WB7
        elif (
            run.attr(-2) in AHLetterTuple
            and run.prev in (WB.MidLetter,) + MidNumLetQTuple
            and run.curr in AHLetterTuple
        ):
            run.do_not_break_here()
        # WB7a
        elif run.prev == WB.Hebrew_Letter and run.curr == WB.Single_Quote:
            run.do_not_break_here()
        # WB7b
        elif (
            run.prev == WB.Hebrew_Letter
            and run.curr == WB.Double_Quote
            and run.next == WB.Hebrew_Letter
        ):
            run.do_not_break_here()
        # WB7c
        elif (
            run.attr(-2) == WB.Hebrew_Letter
            and run.prev == WB.Double_Quote
            and run.curr == WB.Hebrew_Letter
        ):
            run.do_not_break_here()
        # WB8
        elif run.prev == run.curr == WB.Numeric:
            run.do_not_break_here()
        # WB9
        elif run.prev in AHLetterTuple and run.curr == WB.Numeric:
            run.do_not_break_here()
        # WB10
        elif run.prev == WB.Numeric and run.curr in AHLetterTuple:
            run.do_not_break_here()
        # WB11
        elif (
            run.attr(-2) == WB.Numeric
            and run.prev in (WB.MidNum,) + MidNumLetQTuple
            and run.curr == WB.Numeric
        ):
            run.do_not_break_here()
        # WB12
        elif (
            run.prev == WB.Numeric
            and run.curr in (WB.MidNum,) + MidNumLetQTuple
            and run.next == WB.Numeric
        ):
            run.do_not_break_here()
        # WB13
        elif run.prev == run.curr == WB.Katakana:
            run.do_not_break_here()
        # WB13a
        elif (
            run.prev in AHLetterTuple + (WB.Numeric, WB.Katakana, WB.ExtendNumLet)
            and run.curr == WB.ExtendNumLet
        ):
            run.do_not_break_here()
        # WB13b
        elif (
            run.prev == WB.ExtendNumLet
            and run.curr in AHLetterTuple + (WB.Numeric, WB.Katakana)
        ):
            run.do_not_break_here()
    run.head()
    # WB15, WB16
    while 1:
        while run.curr != WB.Regional_Indicator:
            if not run.walk():
                break
        if not run.walk():
            break
        while run.prev == run.curr == WB.Regional_Indicator:
            run.do_not_break_here()
            if not run.walk():
                break
            if not run.walk():
                break
    # WB999
    run.set_default(Breakable.Break)
    return run.literal_breakables()


def word_boundaries(
        s: str, /, tailor: Optional[TailorBreakables] = None
) -> Iterator[int]:
    """Iterate indices of the word boundaries of `s`

    This function yields indices from the first boundary position (> 0)
    to the end of the string (== len(s)).
    """
    breakables = word_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def words(s: str, /, tailor: Optional[TailorBreakables] = None) -> Iterator[str]:
    """Iterate *user-perceived* words of `s`

    These examples bellow is from
    http://www.unicode.org/reports/tr29/tr29-15.html#Word_Boundaries

    >>> s = 'The quick (“brown”) fox can’t jump 32.3 feet, right?'
    >>> '|'.join(words(s))
    'The| |quick| |(|“|brown|”|)| |fox| |can’t| |jump| |32.3| |feet|,| |right|?'
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
