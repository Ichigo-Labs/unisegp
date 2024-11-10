"""Unicode sentence boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

from collections.abc import Iterator
from enum import Enum
from typing import Optional

from uniseg import UnicodeProperty
from uniseg.breaking import (Breakable, Breakables, Run, TailorFunc,
                             boundaries, break_units)
from uniseg.db import sentence_break as _sentence_break

__all__ = [
    'SentenceBreak',
    'SB',
    'sentence_break',
    'sentence_breakables',
    'sentence_boundaries',
    'sentences',
]


class SentenceBreak(UnicodeProperty):
    """Sentence_Break property values."""
    Other = 'Other'
    CR = 'CR'
    LF = 'LF'
    Extend = 'Extend'
    Sep = 'Sep'
    Format = 'Format'
    Sp = 'Sp'
    Lower = 'Lower'
    Upper = 'Upper'
    OLetter = 'OLetter'
    Numeric = 'Numeric'
    ATerm = 'ATerm'
    SContinue = 'SContinue'
    STerm = 'STerm'
    Close = 'Close'


# type alias for `SentenceBreak`
SB = SentenceBreak

ParaSepTuple = (SB.Sep, SB.CR, SB.LF)
SATermTuple = (SB.STerm, SB.ATerm)


def sentence_break(c: str, index: int = 0, /) -> SentenceBreak:
    R"""Return Sentence_Break property value of `c`.

    `c` must be a single Unicode code point string.

    >>> sentence_break('\x0d')
    SentenceBreak.CR
    >>> sentence_break(' ')
    SentenceBreak.Sp
    >>> sentence_break('a')
    SentenceBreak.Lower

    If `index` is specified, this function consider `c` as a unicode
    string and return Sentence_Break property of the code point at
    c[index].

    >>> sentence_break('a\x0d', 1)
    SentenceBreak.CR

    >>> sentence_break('/')
    SentenceBreak.Other
    """
    return SentenceBreak[_sentence_break(c[index])]


def sentence_breakables(s: str, /) -> Breakables:
    R"""Iterate sentence breaking opportunities for every position of
    `s`.

    1 for "break" and 0 for "do not break".  The length of iteration
    will be the same as ``len(s)``.

    >>> from pprint import pprint
    >>> s = 'He said, \u201cAre you going?\u201d John shook his head.'
    >>> pprint(list(sentence_breakables(s)), width=76, compact=True)
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    """
    run = Run(s, sentence_break)
    # SB1
    run.break_here()
    while run.walk():
        # SB3
        if run.prev == SB.CR and run.curr == SB.LF:
            run.do_not_break_here()
        # SB4
        elif run.prev in ParaSepTuple:
            run.break_here()
    # SB5
    run.set_skip_table(x not in (SB.Extend, SB.Format)
                       for x in run.attributes())
    run.head()
    while run.walk():
        # SB6
        if run.prev == SB.ATerm and run.curr == SB.Numeric:
            run.do_not_break_here()
        # SB7
        elif (
            run.attr(-2) in (SB.Upper, SB.Lower)
            and run.prev == SB.ATerm
            and run.curr == SB.Upper
        ):
            run.do_not_break_here()
        # SB8
        elif (
            run.is_following((SB.Sp,), greedy=True)
            .is_following((SB.Close,), greedy=True).prev == SB.ATerm
            and (
                (
                    run.curr in (SB.Extend, SB.Format, SB.Sp,
                                 SB.Numeric, SB.SContinue, SB.Close)
                    and run.is_leading((SB.Extend, SB.Format, SB.Sp, SB.Numeric,
                                        SB.SContinue, SB.Close), greedy=True)
                    .next == SB.Lower
                )
                or run.curr == SB.Lower
            )
        ):
            run.do_not_break_here()
        # SB8a
        elif (
            run.is_following((SB.Sp,), greedy=True)
            .is_following((SB.Close,), greedy=True).prev in SATermTuple
            and run.curr in (SB.SContinue,) + SATermTuple
        ):
            run.do_not_break_here()
        # SB9
        elif (
            run.is_following((SB.Close,), greedy=True).prev in SATermTuple
            and run.curr in (SB.Close, SB.Sp) + ParaSepTuple
        ):
            run.do_not_break_here()
        # SB10
        elif (
            run.is_following((SB.Sp,), greedy=True)
            .is_following((SB.Close,), greedy=True).prev in SATermTuple
            and run.curr in (SB.Sp,) + ParaSepTuple
        ):
            run.do_not_break_here()
        # SB11
        elif (
            run.is_following((SB.Sp,), greedy=True)
            .is_following((SB.Close,), greedy=True).prev in SATermTuple
            or run.is_following(ParaSepTuple, noskip=True)
            .is_following((SB.Sp,), greedy=True)
            .is_following((SB.Close,), greedy=True).prev in SATermTuple
        ):
            run.break_here()
        else:
            run.do_not_break_here()
    # SB998
    run.set_default(Breakable.DoNotBreak)
    return run.literal_breakables()


def sentence_boundaries(s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[int]:
    R"""Iterate indices of the sentence boundaries of `s`.

    This function yields from 0 to the end of the string (== len(s)).

    >>> list(sentence_boundaries('ABC'))
    [0, 3]
    >>> s = 'He said, \u201cAre you going?\u201d John shook his head.'
    >>> list(sentence_boundaries(s))
    [0, 26, 46]
    >>> list(sentence_boundaries(''))
    []
    """
    breakables = sentence_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def sentences(s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[str]:
    R"""Iterate every sentence of `s`.

    >>> s = 'He said, \u201cAre you going?\u201d John shook his head.'
    >>> list(sentences(s)) == ['He said, \u201cAre you going?\u201d ', 'John shook his head.']
    True
    """
    breakables = sentence_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
