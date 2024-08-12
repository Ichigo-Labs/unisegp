"""Unicode sentence boundaries.

UAX #29: Unicode Text Segmentation (Unicode 15.0.0)
https://www.unicode.org/reports/tr29/tr29-41.html
"""

from enum import Enum
from typing import Iterator, Optional, Tuple, Sequence, List

from uniseg.breaking import boundaries, break_units, Breakables, TailorFunc
from uniseg.codepoint import code_point, code_points
from uniseg.db import sentence_break as _sentence_break


__all__ = [
    'SentenceBreak',
    'SB',
    'sentence_break',
    'sentence_breakables',
    'sentence_boundaries',
    'sentences',
]


class SentenceBreak(Enum):
    """Sentence_Break property values. """

    OTHER = 'Other'
    CR = 'CR'
    LF = 'LF'
    EXTEND = 'Extend'
    SEP = 'Sep'
    FORMAT = 'Format'
    SP = 'Sp'
    LOWER = 'Lower'
    UPPER = 'Upper'
    OLETTER = 'OLetter'
    NUMERIC = 'Numeric'
    ATERM = 'ATerm'
    SCONTINUE = 'SContinue'
    STERM = 'STerm'
    CLOSE = 'Close'


# type alias for `SentenceBreak`
SB = SentenceBreak


def sentence_break(c: str, index: int = 0, /) -> SentenceBreak:

    r"""Return Sentence_Break property value of `c`

    `c` must be a single Unicode code point string.

    >>> sentence_break('\x0d')
    <SentenceBreak.CR: 'CR'>
    >>> sentence_break(' ')
    <SentenceBreak.SP: 'Sp'>
    >>> sentence_break('a')
    <SentenceBreak.LOWER: 'Lower'>

    If `index` is specified, this function consider `c` as a unicode
    string and return Sentence_Break property of the code point at
    c[index].

    >>> sentence_break('a\x0d', 1)
    <SentenceBreak.CR: 'CR'>

    >>> sentence_break('/')
    <SentenceBreak.OTHER: 'Other'>
    """

    return SentenceBreak[_sentence_break(code_point(c, index)).upper()]


def _preprocess_boundaries(s: str, /) -> Iterator[Tuple[int, SentenceBreak]]:

    r"""(internal)

    >>> from pprint import pprint
    >>> pprint(list(_preprocess_boundaries('Aa')),
    ...        width=76, compact=True)
    [(0, <SentenceBreak.UPPER: 'Upper'>), (1, <SentenceBreak.LOWER: 'Lower'>)]
    >>> pprint(list(_preprocess_boundaries('A a')),
    ...        width=76, compact=True)
    [(0, <SentenceBreak.UPPER: 'Upper'>), (1, <SentenceBreak.SP: 'Sp'>),
     (2, <SentenceBreak.LOWER: 'Lower'>)]
    >>> pprint(list(_preprocess_boundaries('A" a')),
    ...        width=76, compact=True)
    [(0, <SentenceBreak.UPPER: 'Upper'>), (1, <SentenceBreak.CLOSE: 'Close'>),
     (2, <SentenceBreak.SP: 'Sp'>), (3, <SentenceBreak.LOWER: 'Lower'>)]
    >>> pprint(list(_preprocess_boundaries('A\xad "')),
    ...        width=76, compact=True)
    [(0, <SentenceBreak.UPPER: 'Upper'>), (2, <SentenceBreak.SP: 'Sp'>),
     (3, <SentenceBreak.CLOSE: 'Close'>)]
    >>> pprint(list(_preprocess_boundaries('\r\rA')),
    ...        width=76, compact=True)
    [(0, <SentenceBreak.CR: 'CR'>), (1, <SentenceBreak.CR: 'CR'>),
     (2, <SentenceBreak.UPPER: 'Upper'>)]
    """

    prev_prop = None
    i = 0
    for c in code_points(s):
        prop = sentence_break(c)
        if prop in (SB.SEP, SB.CR, SB.LF):
            yield (i, prop)
            prev_prop = None
        elif prop in (SB.EXTEND, SB.FORMAT):
            if prev_prop is None:
                yield (i, prop)
                prev_prop = prop
        elif prev_prop != prop:
            yield (i, prop)
            prev_prop = prop
        i += len(c)


def _next_break(primitive_boundaries: Sequence[Tuple[int, SentenceBreak]],
                pos: int,
                expects: Sequence[SentenceBreak], /) -> Optional[SentenceBreak]:

    """(internal)
    """

    for i in range(pos, len(primitive_boundaries)):
        sb = primitive_boundaries[i][1]
        if sb in expects:
            return sb
    return None


def sentence_breakables(s: str, /) -> Breakables:

    r"""Iterate sentence breaking opportunities for every position of
    `s`

    1 for "break" and 0 for "do not break".  The length of iteration
    will be the same as ``len(s)``.

    >>> from pprint import pprint
    >>> s = 'He said, \u201cAre you going?\u201d John shook his head.'
    >>> pprint(list(sentence_breakables(s)),
    ...        width=76, compact=True)
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    """

    primitive_boundaries = list(_preprocess_boundaries(s))
    prev_prev_prev_prev_sb = None
    prev_prev_prev_sb = None
    prev_prev_sb = None
    prev_sb = None
    pos = 0
    for i, (pos, sb) in enumerate(primitive_boundaries):
        next_pos, next_sb = (primitive_boundaries[i+1]
                             if i<len(primitive_boundaries)-1 else (len(s), None))
        if pos == 0:
            do_break = True
        # SB3
        elif prev_sb == SB.CR and sb == SB.LF:
            do_break = False
        # SB4
        elif prev_sb in (SB.SEP, SB.CR, SB.LF):
            do_break = True
        # SB6
        elif prev_sb == SB.ATERM and sb == SB.NUMERIC:
            do_break = False
        # SB7
        elif prev_prev_sb == SB.UPPER and prev_sb == SB.ATERM and sb == SB.UPPER:
            do_break = False
        # SB8
        elif (((prev_sb == SB.ATERM)
               or (prev_prev_sb == SB.ATERM and prev_sb == SB.CLOSE)
               or (prev_prev_sb == SB.ATERM and prev_sb == SB.SP)
               or (prev_prev_prev_sb == SB.ATERM and prev_prev_sb == SB.CLOSE
                   and prev_sb == SB.SP))
              and _next_break(primitive_boundaries, i,
                              [SB.OLETTER, SB.UPPER, SB.LOWER, SB.SEP, SB.CR,
                               SB.LF, SB.STERM, SB.ATERM]) == SB.LOWER):
            do_break = False
        # SB8a
        elif ( (
            (prev_sb in (SB.STERM, SB.ATERM))
            or (prev_prev_sb in (SB.STERM, SB.ATERM) and prev_sb == SB.CLOSE)
            or (prev_prev_sb in (SB.STERM, SB.ATERM) and prev_sb == SB.SP)
            or (prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                and prev_prev_sb == SB.CLOSE and prev_sb == SB.SP)
        ) and (
            sb in (SB.SCONTINUE, SB.STERM, SB.ATERM)
        ) ):
            do_break = False
        # SB9
        elif (((prev_sb in (SB.STERM, SB.ATERM))
               or (prev_prev_sb in (SB.STERM, SB.ATERM) and prev_sb == SB.CLOSE))
              and sb in (SB.CLOSE, SB.SP, SB.SEP, SB.CR, SB.LF)):
            do_break = False
        # SB10
        elif (((prev_sb in (SB.STERM, SB.ATERM))
               or (prev_prev_sb in (SB.STERM, SB.ATERM) and prev_sb == SB.CLOSE)
               or (prev_prev_sb in (SB.STERM, SB.ATERM) and prev_sb == SB.SP)
               or (prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_prev_sb == SB.CLOSE
                   and prev_sb == SB.SP))
              and sb in (SB.SP, SB.SEP, SB.CR, SB.LF)):
            do_break = False
        # SB11
        elif ((prev_sb in (SB.STERM, SB.ATERM))
               or (prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_sb == SB.CLOSE)
               or (prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_sb == SB.SP)
               or (prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_sb in (SB.SEP, SB.CR, SB.LF))
               or (prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_prev_sb == SB.CLOSE
                   and prev_sb == SB.SP)
               or (prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_prev_sb == SB.CLOSE
                   and prev_sb in (SB.SEP, SB.CR, SB.LF))
               or (prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_prev_sb == SB.SP
                   and prev_sb in (SB.SEP, SB.CR, SB.LF))
               or (prev_prev_prev_prev_sb in (SB.STERM, SB.ATERM)
                   and prev_prev_prev_sb == SB.CLOSE
                   and prev_prev_sb == SB.SP
                   and prev_sb in (SB.SEP, SB.CR, SB.LF))):
            do_break = True
        else:
            do_break = False
        for j in range(next_pos-pos):
            yield 1 if j==0 and do_break else 0
        prev_prev_prev_prev_sb = prev_prev_prev_sb
        prev_prev_prev_sb = prev_prev_sb
        prev_prev_sb = prev_sb
        prev_sb = sb
        pos = next_pos


def sentence_boundaries(s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[int]:

    r"""Iterate indices of the sentence boundaries of `s`

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

    r"""Iterate every sentence of `s`

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
