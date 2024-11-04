"""Unicode line breaking algorithm.

UAX #14: Unicode Line Breaking Algorithm (Unicode 16.0.0)
https://www.unicode.org/reports/tr14/tr14-53.html
"""

from collections.abc import Iterator
from enum import Enum
from sys import stderr
from typing import Iterable, Optional
from unicodedata import east_asian_width, category

from uniseg.db import extended_pictographic
from uniseg.breaking import (Breakable, Breakables, Run, TailorFunc,
                             boundaries, break_units)
from uniseg.db import line_break as _line_break

__all__ = [
    'line_break',
    'line_break_breakables',
    'line_break_boundaries',
    'line_break_units',
]


class LineBreak(Enum):
    """Line_Break property values."""
    BK = 'BK'   # Mandatory Break
    CR = 'CR'   # Carriage Return
    LF = 'LF'   # Line Feed
    CM = 'CM'   # Combining Mark
    NL = 'NL'   # Next Line
    SG = 'SG'   # Surrogate
    WJ = 'WJ'   # Word Joiner
    ZW = 'ZW'   # Zero Width Space
    GL = 'GL'   # Non-breaking ("Glue")
    SP = 'SP'   # Space
    ZWJ = 'ZWJ'  # Zero Width Joiner
    B2 = 'B2'   # Break Opportunity Before and After
    BA = 'BA'   # Break After
    BB = 'BB'   # Break Before
    HY = 'HY'   # Hyphen
    CB = 'CB'   # Contingent Break Opportunity
    CL = 'CL'   # Close Punctuation
    CP = 'CP'   # Close Parenthesis
    EX = 'EX'   # Exclamation/Interrogation
    IN = 'IN'   # Inseparable
    NS = 'NS'   # Nonstarter
    OP = 'OP'   # Open Punctuation
    QU = 'QU'   # Quotation
    IS = 'IS'   # Infix Numeric Separator
    NU = 'NU'   # Numeric
    PO = 'PO'   # Postfix Numeric
    PR = 'PR'   # Prefix Numeric
    SY = 'SY'   # Symbols Allowing Break After
    AI = 'AI'   # Ambiguous (Alphabetic or Ideographic)
    AK = 'AK'   # Aksara
    AL = 'AL'   # Alphabetic
    AP = 'AP'   # Aksara Pre-Base
    AS = 'AS'   # Aksara Start
    CJ = 'CJ'   # Conditional Japanese Starter
    EB = 'EB'   # Emoji Base
    EM = 'EM'   # Emoji Modifier
    H2 = 'H2'   # Hangul LV Syllable
    H3 = 'H3'   # Hangul LVT Syllable
    HL = 'HL'   # Hebrew Letter
    ID = 'ID'   # Ideographic
    JL = 'JL'   # Hangul L Jamo
    JV = 'JV'   # Hangul V Jamo
    JT = 'JT'   # Hangul T Jamo
    RI = 'RI'   # Regional Indicator
    SA = 'SA'   # Complex Context Dependent (South East Asian)
    VF = 'VF'   # Virama Final
    VI = 'VI'   # Virama
    XX = 'XX'   # Unknown


# type alias for `LineBreak`
LB = LineBreak


EastAsianTuple = ('F', 'W', 'H')


def line_break(c: str, index: int = 0, /) -> LineBreak:
    R"""Return the Line_Break property for `c`.

    `c` must be a single Unicode code point string.

    >>> line_break('\x0d')
    <LineBreak.CR: 'CR'>
    >>> line_break(' ')
    <LineBreak.SP: 'SP'>
    >>> line_break('1')
    <LineBreak.NU: 'NU'>
    >>> line_break('\u1b44)
    <LineBreak.VI: 'VI'>

    If `index` is specified, this function consider `c` as a unicode
    string and return Line_Break property of the code point at
    c[index].

    >>> line_break('a\x0d', 1)
    <LineBreak.CR: 'CR'>
    """

    return LineBreak[_line_break(c[index])]


def resolve_lb1_linebreak(ch: str, /) -> LineBreak:
    lb = line_break(ch)
    cat = category(ch)
    if lb in (LB.AI, LB.SG, LB.XX):
        lb = LB.AL
    elif lb == LB.SA:
        if cat in ('Mn', 'Mc'):
            lb = LB.CM
        else:
            lb = LB.AL
    elif lb == LB.CJ:
        lb = LB.NS
    return lb


def line_break_breakables(s: str, legacy: bool = False, /) -> Breakables:
    """Iterate line breaking opportunities for every position of `s`

    1 means "break" and 0 means "do not break" BEFORE the postion.
    The length of iteration will be the same as ``len(s)``.

    >>> list(line_break_breakables('ABC'))
    [0, 0, 0]
    >>> list(line_break_breakables('Hello, world.'))
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    >>> list(line_break_breakables(''))
    []
    """
    if not s:
        return iter([])

    # LB1
    run = Run(s, resolve_lb1_linebreak)
    # LB2
    run.do_not_break_here()
    while run.walk():
        # LB4
        if run.prev == LB.BK:
            run.break_here()
        # LB5
        elif run.prev == LB.CR and run.curr == LB.LF:
            run.do_not_break_here()
        elif run.prev in (LB.CR, LB.LF, LB.NL):
            run.break_here()
        # LB6
        elif run.curr in (LB.BK, LB.CR, LB.LF, LB.NL):
            run.do_not_break_here()
        # LB7
        elif run.curr in (LB.SP, LB.ZW):
            run.do_not_break_here()
        # LB8
        elif run.is_following((LB.SP,), greedy=True).prev == LB.ZW:
            run.break_here()
        # LB8a
        elif run.prev == LB.ZWJ:
            run.do_not_break_here()
    # LB9
    run.head()
    skip_table = [1]
    while run.walk():
        if (
            run.is_following((LB.CM, LB.ZWJ), greedy=True).prev not in (
                LB.BK, LB.CR, LB.LF, LB.NL, LB.SP, LB.ZW)
            and run.curr in (LB.CM, LB.ZWJ)

        ):
            skip_table.append(0)
            run.do_not_break_here()
        else:
            skip_table.append(1)
    run.set_skip_table(skip_table)
    # LB10
    run.head()
    while 1:
        if run.curr in (LB.CM, LB.ZWJ):
            run.set_char('A')
            run.set_attr(LB.AL)
        if not run.walk():
            break
    run.head()
    while run.walk():
        # LB11
        if run.curr == LB.WJ or run.prev == LB.WJ:
            run.do_not_break_here()
        # LB12
        elif run.prev == LB.GL:
            run.do_not_break_here()
        # LB12a
        elif run.prev not in (LB.SP, LB.BA, LB.HY) and run.curr == LB.GL:
            run.do_not_break_here()
        # LB13
        elif run.curr in (LB.CL, LB.CP, LB.EX, LB.SY):
            run.do_not_break_here()
        # LB14
        elif run.is_following((LB.SP,), greedy=True).prev == LB.OP:
            run.do_not_break_here()
        # LB15a
        elif (
            (
                (run0 := run.is_following((LB.SP,), greedy=True))
                and (run0.pc and category(run0.pc) == 'Pi')
            )
            and (
                (run1 := run0.is_following((LB.QU,))).prev in (
                    LB.BK, LB.CR, LB.LF, LB.NL, LB.OP, LB.QU, LB.GL, LB.SP, LB.ZW)
                or run1.is_sot()
            )
        ):
            run.do_not_break_here()
        # LB15b
        elif (
            run.cc and category(run.cc) == 'Pf' and run.curr == LB.QU
            and (
                run.is_leading((LB.SP, LB.GL, LB.WJ, LB.CL, LB.QU, LB.CP,
                                LB.EX, LB.IS, LB.SY, LB.BK, LB.CR, LB.LF, LB.NL, LB.ZW))
                or run.is_eot()
            )
        ):
            run.do_not_break_here()
        # LB15c
        elif run.prev == LB.SP and run.curr == LB.IS and run.next == LB.NU:
            run.break_here()
        # LB15d
        elif run.curr == LB.IS:
            run.do_not_break_here()
        # LB16
        elif (
            run.is_following((LB.SP,), greedy=True).prev in (LB.CL, LB.CP)
            and run.curr == LB.NS
        ):
            run.do_not_break_here()
        # LB17
        elif (
            run.is_following((LB.SP,), greedy=True).prev == LB.B2
            and run.curr == LB.B2
        ):
            run.do_not_break_here()
        # LB18
        elif run.prev == LB.SP:
            run.break_here()
        # LB19
        elif (
            (run.curr == LB.QU and run.cc and category(run.cc) != 'Pi')
            or (run.prev == LB.QU and run.pc and category(run.pc) != 'Pi')
        ):
            run.do_not_break_here()
        # LB19a
        elif (
            (
                (run.pc and east_asian_width(run.pc) not in EastAsianTuple)
                and run.curr == LB.QU
            )
            or (
                run.curr == LB.QU
                and (
                    (run.nc and east_asian_width(run.nc) not in EastAsianTuple)
                    or run.is_eot()
                )
            )
            or (
                run.prev == LB.QU
                and (run.cc and east_asian_width(run.cc) not in EastAsianTuple)
            )
            or (
                run0 := run.is_following((LB.QU,))
                and (
                    (run0.pc and east_asian_width(run0.pc) not in EastAsianTuple)
                    or run0.is_sot
                )
            )
        ):
            run.do_not_break_here()
        # LB20
        elif run.curr == LB.CB or run.prev == LB.CB:
            run.break_here()
        # LB20a
        elif (
            (run0 := run.is_following((LB.HY, LB.BA)))
            and (
                run0.prev in (LB.BK, LB.CR, LB.LF, LB.NL,
                              LB.SP, LB.ZW, LB.CB, LB.GL)
                or run0.is_sot()
            )
            and run.curr == LB.AL
            and (run.prev == LB.HY or run.pc == '\u2010')
        ):
            run.do_not_break_here()
        # LB21
        elif run.curr in (LB.BA, LB.HY, LB.NS) or run.prev == LB.BB:
            run.do_not_break_here()
        # LB21a
        elif run.is_following((LB.HY, LB.BA)).prev == LB.HL and run.curr != LB.HL:
            run.do_not_break_here()
        # LB21b
        elif run.prev == LB.SY and run.curr == LB.HL:
            run.do_not_break_here()
        # LB22
        elif run.curr == LB.IN:
            run.do_not_break_here()
        # LB23
        elif (
            (run.prev in (LB.AL, LB.HL) and run.curr == LB.NU)
            or (run.prev == LB.NU and run.curr in (LB.AL, LB.HL))
        ):
            run.do_not_break_here()
        # LB23a
        elif (
            (run.prev == LB.PR and run.curr in (LB.ID, LB.EB, LB.EM))
            or (run.prev in (LB.ID, LB.EB, LB.EM) and run.curr == LB.PO)
        ):
            run.do_not_break_here()
        # LB24
        elif (
            (run.prev in (LB.PR, LB.PO) and run.curr in (LB.AL, LB.HL))
            or (run.prev in (LB.AL, LB.HL) and run.curr in (LB.PR, LB.PO))
        ):
            run.do_not_break_here()
        # LB25
        elif (
            (run.is_following((LB.CL, LB.CP)).is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
             and run.curr in (LB.PO, LB.PR))
            or (run.is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
                and run.curr in (LB.PO, LB.PR))
            or (run.prev in (LB.PO, LB.PR) and run.curr == LB.OP and run.next == LB.NU)
            or (run.prev in (LB.PO, LB.PR) and run.curr == LB.OP and run.next == LB.IS
                and run.attr(2) == LB.NU)
            or (run.prev in (LB.PO, LB.PR) and run.curr == LB.NU)
            or (run.prev in (LB.HY, LB.IS) and run.curr == LB.NU)
            or (run.is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
                and run.curr == LB.NU)
        ):
            run.do_not_break_here()
        # LB26
        elif (
            (run.prev == LB.JL and run.curr in (LB.JL, LB.JV, LB.H2, LB.H3))
            or (run.prev in (LB.JV, LB.H2) and run.curr in (LB.JV, LB.JT))
            or (run.prev in (LB.JT, LB.H3) and run.curr == LB.JT)
        ):
            run.do_not_break_here()
        # LB27
        elif (
            (run.prev in (LB.JL, LB.JV, LB.JT, LB.H2, LB.H3) and run.curr == LB.PO)
            or (run.prev == LB.PR and run.curr in (LB.JL, LB.JV, LB.JT, LB.H2, LB.H3))
        ):
            run.do_not_break_here()
        # LB28
        elif run.prev in (LB.AL, LB.HL) and run.curr in (LB.AL, LB.HL):
            run.do_not_break_here()
        # LB28a
        elif (
            (
                run.prev == LB.AP
                and (run.curr in (LB.AK, LB.AS) or run.cc == '\u25cc')
            )
            or (
                (run.prev in (LB.AK, LB.AS) or run.pc == '\u25cc')
                and run.curr in (LB.VF, LB.VI)
            )
            or (
                (run.attr(-2) in (LB.AK, LB.AS) or run.char(-2) == '\u25cc')
                and run.prev == LB.VI
                and (run.curr == LB.AK or run.cc == '\u25cc')
            )
            or (
                (run.prev in (LB.AK, LB.AS) or run.pc == '\u25cc')
                and (run.curr in (LB.AK, LB.AS) or run.cc == '\u25cc')
                and run.next == LB.VF
            )
        ):
            run.do_not_break_here()
        # LB29
        elif run.prev == LB.IS and run.curr in (LB.AL, LB.HL):
            run.do_not_break_here()
        # LB30
        elif (
            (
                run.prev in (LB.AL, LB.HL, LB.NU) and run.curr == LB.OP
                and run.cc and east_asian_width(run.cc) not in EastAsianTuple
            )
            or (
                run.prev == LB.CP
                and run.pc and east_asian_width(run.pc) not in EastAsianTuple
                and run.curr in (LB.AL, LB.HL, LB.NU)
            )
        ):
            run.do_not_break_here()
    # LB30a
    run.head()
    while 1:
        while run.curr != LB.RI:
            if not run.walk():
                break
        if not run.walk():
            break
        while run.prev == run.curr == LB.RI:
            run.do_not_break_here()
            if not run.walk():
                break
            if not run.walk():
                break
    # LB30b
    run.head()
    while run.walk():
        if (
            (run.prev == LB.EB and run.curr == LB.EM)
            or (
                run.pc and category(run.pc) == 'Cn'
                and extended_pictographic(run.pc) and run.curr == LB.EM
            )
        ):
            run.do_not_break_here()
    # LB31
    # print(run.attributes(), file=stderr)
    # print(run.breakables(), file=stderr)
    # print(run._skip_table, file=stderr)
    run.set_default(Breakable.Break)
    return run.literal_breakables()


def line_break_boundaries(s: str,
                          legacy: bool = False,
                          tailor: Optional[TailorFunc] = None) -> Iterator[int]:
    """Iterate indices of the line breaking boundaries of `s`

    This function yields from 0 to the end of the string (== len(s)).
    """

    breakables = line_break_breakables(s, legacy)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def line_break_units(s: str,
                     legacy: bool = False,
                     tailor: Optional[TailorFunc] = None, /) -> Iterator[str]:
    r"""Iterate every line breaking token of `s`

    >>> s = 'The quick (\u201cbrown\u201d) fox can\u2019t jump 32.3 feet, right?'
    >>> '|'.join(line_break_units(s)) == 'The |quick |(\u201cbrown\u201d) |fox |can\u2019t |jump |32.3 |feet, |right?'
    True
    >>> list(line_break_units(''))
    []

    >>> list(line_break_units('\u03b1\u03b1')) == ['\u03b1\u03b1']
    True
    >>> list(line_break_units('\u03b1\u03b1', True)) == ['\u03b1', '\u03b1']
    True
    """

    breakables = line_break_breakables(s, legacy)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
