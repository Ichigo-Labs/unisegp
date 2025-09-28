"""Unicode line breaking algorithm.

`UAX #14: Unicode Line Breaking Algorithm (Unicode 16.0.0)
<https://www.unicode.org/reports/tr14/tr14-53.html>`_
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Optional

from uniseg import Unicode_Property
from uniseg.breaking import (Breakable, Breakables, Run, TailorBreakables, boundaries,
                             break_units)
from uniseg.db import get_handle, get_value
from uniseg.emoji import extended_pictographic
from uniseg.unicodedata_ import (EA, GC, East_Asian_Width, General_Category,
                                 east_asian_width_, general_category_)

__all__ = [
    'Line_Break',
    'LB',
    'line_break',
    'line_break_breakables',
    'line_break_boundaries',
    'line_break_units',
]

H_LINE_BREAK = get_handle('Line_Break')


class Line_Break(Unicode_Property):
    """Line_Break property values."""
    BK = 'BK'
    """Line_Break property value BK, Mandatory Break"""
    CR = 'CR'
    """Line_Break property value CR, Carriage Return"""
    LF = 'LF'
    """Line_Break property value LF, Line Feed"""
    CM = 'CM'
    """Line_Break property value CM, Combining Mark"""
    NL = 'NL'
    """Line_Break property value NL, Next Line"""
    SG = 'SG'
    """Line_Break property value SG, Surrogate"""
    WJ = 'WJ'
    """Line_Break property value WJ, Word Joiner"""
    ZW = 'ZW'
    """Line_Break property value ZW, Zero Width Space"""
    GL = 'GL'
    """Line_Break property value GL, Non-breaking ("Glue")"""
    SP = 'SP'
    """Line_Break property value SP, Space"""
    ZWJ = 'ZWJ'
    """ZLine_Break property value ZWJ, Zero Width Joiner"""
    B2 = 'B2'
    """Line_Break property value B2, Break Opportunity Before and After"""
    BA = 'BA'
    """Line_Break property value BA, Break After"""
    BB = 'BB'
    """Line_Break property value BB, Break Before"""
    HY = 'HY'
    """Line_Break property value HY, Hyphen"""
    CB = 'CB'
    """Line_Break property value CB, Contingent Break Opportunity"""
    CL = 'CL'
    """Line_Break property value CL, Close Punctuation"""
    CP = 'CP'
    """Line_Break property value CP, Close Parenthesis"""
    EX = 'EX'
    """Line_Break property value EX, Exclamation/Interrogation"""
    IN = 'IN'
    """Line_Break property value IN, Inseparable"""
    NS = 'NS'
    """Line_Break property value NS, Nonstarter"""
    OP = 'OP'
    """Line_Break property value OP, Open Punctuation"""
    QU = 'QU'
    """Line_Break property value QU, Quotation"""
    IS = 'IS'
    """Line_Break property value IS, Infix Numeric Separator"""
    NU = 'NU'
    """Line_Break property value NU, Numeric"""
    PO = 'PO'
    """Line_Break property value PO, Postfix Numeric"""
    PR = 'PR'
    """Line_Break property value PR, Prefix Numeric"""
    SY = 'SY'
    """Line_Break property value SY, Symbols Allowing Break After"""
    AI = 'AI'
    """Line_Break property value AI, Ambiguous (Alphabetic or Ideographic)"""
    AK = 'AK'
    """Line_Break property value AK, Aksara"""
    AL = 'AL'
    """Line_Break property value AL, Alphabetic"""
    AP = 'AP'
    """Line_Break property value AP, Aksara Pre-Base"""
    AS = 'AS'
    """Line_Break property value AS, Aksara Start"""
    CJ = 'CJ'
    """Line_Break property value CJ, Conditional Japanese Starter"""
    EB = 'EB'
    """Line_Break property value EB, Emoji Base"""
    EM = 'EM'
    """Line_Break property value EM, Emoji Modifier"""
    H2 = 'H2'
    """Line_Break property value H2, Hangul LV Syllable"""
    H3 = 'H3'
    """Line_Break property value H3, Hangul LVT Syllable"""
    HL = 'HL'
    """Line_Break property value HL, Hebrew Letter"""
    ID = 'ID'
    """Line_Break property value ID, Ideographic"""
    JL = 'JL'
    """Line_Break property value JL, Hangul L Jamo"""
    JV = 'JV'
    """Line_Break property value JV, Hangul V Jamo"""
    JT = 'JT'
    """Line_Break property value JT, Hangul T Jamo"""
    RI = 'RI'
    """Line_Break property value RI, Regional Indicator"""
    SA = 'SA'
    """Line_Break property value SA, Complex Context Dependent (South East Asian)"""
    VF = 'VF'
    """Line_Break property value VF, Virama Final"""
    VI = 'VI'
    """Line_Break property value VI, Virama"""
    XX = 'XX'
    """Line_Break property value XX, Unknown"""


# type alias for `LineBreak`
LB = Line_Break


EastAsianTuple = (EA.F, EA.W, EA.H)


def line_break(c: str, /) -> Line_Break:
    R"""Return the Line_Break property for `c`.

    `c` must be a single Unicode code point string.

    >>> line_break('\r')
    Line_Break.CR
    >>> line_break(' ')
    Line_Break.SP
    >>> line_break('1')
    Line_Break.NU
    >>> line_break('᭄') # (== '\u1b44')
    Line_Break.VI
    """
    return Line_Break[get_value(H_LINE_BREAK, ord(c)) or 'XX']


def _ea(c: Optional[str], /) -> Optional[East_Asian_Width]:
    return None if c is None else east_asian_width_(c)


def _cat(c: Optional[str], /) -> Optional[General_Category]:
    return None if c is None else general_category_(c)


def _extpict(c: Optional[str], /) -> Optional[bool]:
    return False if c is None else extended_pictographic(c)


def resolve_lb1_linebreak(c: str, /) -> Line_Break:
    lb = line_break(c)
    cat = general_category_(c)
    if lb in (LB.AI, LB.SG, LB.XX):
        lb = LB.AL
    elif lb == LB.SA:
        if cat in (GC.Mn, GC.Mc):
            lb = LB.CM
        else:
            lb = LB.AL
    elif lb == LB.CJ:
        lb = LB.NS
    return lb


def line_break_breakables(s: str, /, legacy: bool = False) -> Breakables:
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
    if legacy:
        while 1:
            if _ea(run.cc) == EA.A:
                run.set_attr(LB.ID)
            if not run.walk():
                break
        run.head()
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
        elif run.is_following(LB.SP, greedy=True).prev == LB.ZW:
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
        elif run.is_following(LB.SP, greedy=True).prev == LB.OP:
            run.do_not_break_here()
        # LB15a
        elif (
            (run0 := run.is_following(LB.SP, greedy=True))
            and _cat(run0.pc) == GC.Pi
            and (
                (run1 := run0.is_following(LB.QU))
                .prev in (LB.BK, LB.CR, LB.LF, LB.NL, LB.OP,
                          LB.QU, LB.GL, LB.SP, LB.ZW)
                or run1.is_sot()
            )
        ):
            run.do_not_break_here()
        # LB15b
        elif (
            _cat(run.cc) == GC.Pf
            and run.curr == LB.QU
            and (
                run.is_leading((
                    LB.SP, LB.GL, LB.WJ, LB.CL, LB.QU, LB.CP, LB.EX,
                    LB.IS, LB.SY, LB.BK, LB.CR, LB.LF, LB.NL, LB.ZW
                ))
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
            run.is_following(LB.SP, greedy=True).prev in (LB.CL, LB.CP)
            and run.curr == LB.NS
        ):
            run.do_not_break_here()
        # LB17
        elif (
            run.is_following(LB.SP, greedy=True).prev == LB.B2
            and run.curr == LB.B2
        ):
            run.do_not_break_here()
        # LB18
        elif run.prev == LB.SP:
            run.break_here()
        # LB19
        elif (
            (run.curr == LB.QU and _cat(run.cc) != GC.Pi)
            or (run.prev == LB.QU and _cat(run.pc) != GC.Pf)
        ):
            run.do_not_break_here()
        # LB19a
        elif (
            (
                _ea(run.pc) not in EastAsianTuple and run.curr == LB.QU
            )
            or (
                run.curr == LB.QU
                and (_ea(run.nc) not in EastAsianTuple or run.is_eot())
            )
            or (
                run.prev == LB.QU
                and _ea(run.cc) not in EastAsianTuple
            )
            or (
                (run0 := run.is_following(LB.QU))
                and (_ea(run0.pc) not in EastAsianTuple or run0.is_sot())
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
            (run.is_following((LB.CL, LB.CP))
             .is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
             and run.curr in (LB.PO, LB.PR))
            or (
                run.is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
                and run.curr in (LB.PO, LB.PR)
            )
            or (
                run.prev in (LB.PO, LB.PR)
                and run.curr == LB.OP
                and run.next == LB.NU
            )
            or (
                run.prev in (LB.PO, LB.PR)
                and run.curr == LB.OP
                and run.next == LB.IS
                and run.attr(2) == LB.NU
            )
            or (run.prev in (LB.PO, LB.PR) and run.curr == LB.NU)
            or (run.prev in (LB.HY, LB.IS) and run.curr == LB.NU)
            or (
                run.is_following((LB.SY, LB.IS), greedy=True).prev == LB.NU
                and run.curr == LB.NU
            )
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
            (
                run.prev in (LB.JL, LB.JV, LB.JT, LB.H2, LB.H3)
                and run.curr == LB.PO
            )
            or (
                run.prev == LB.PR
                and run.curr in (LB.JL, LB.JV, LB.JT, LB.H2, LB.H3)
            )
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
                run.prev in (LB.AL, LB.HL, LB.NU)
                and run.curr == LB.OP
                and _ea(run.cc) not in EastAsianTuple
            )
            or (
                run.prev == LB.CP
                and _ea(run.pc) not in EastAsianTuple
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
            or (_cat(run.pc) == GC.Cn and _extpict(run.pc) and run.curr == LB.EM)
        ):
            run.do_not_break_here()
    # LB31
    run.set_default(Breakable.Break)
    return run.literal_breakables()


def line_break_boundaries(
    s: str, /, legacy: bool = False, tailor: Optional[TailorBreakables] = None
) -> Iterator[int]:
    R"""Iterate indices of the line breaking boundaries for `s`.

    This function iterates values from 0, which is the start of the string, to
    the end boundary of the string which its value is ``len(s)``.

    >>> list(line_break_boundaries('a'))
    [1]
    >>> list(line_break_boundaries('a b'))
    [2, 3]
    >>> list(line_break_boundaries('a b\n'))
    [2, 4]
    >>> list(line_break_boundaries('あい、うえ、お。'))
    [1, 3, 4, 6, 8]

    The length of the returned list means the count of the line break units for
    the string.
    """

    breakables = line_break_breakables(s, legacy)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def line_break_units(
    s: str, /, legacy: bool = False, tailor: Optional[TailorBreakables] = None
) -> Iterator[str]:
    R"""Iterate every line breaking token of `s`

    >>> s = 'The quick (“brown”) fox can’t jump 32.3 feet, right?'
    >>> '|'.join(line_break_units(s))
    'The |quick |(“brown”) |fox |can’t |jump |32.3 |feet, |right?'
    >>> list(line_break_units(''))
    []

    >>> list(line_break_units('αα'))
    ['αα']
    >>> list(line_break_units('αα', True))
    ['α', 'α']
    """
    breakables = line_break_breakables(s, legacy)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
