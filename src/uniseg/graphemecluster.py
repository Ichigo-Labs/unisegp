"""Unicode grapheme cluster boundaries.

`UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
<https://www.unicode.org/reports/tr29/tr29-45.html>`_
"""

from typing import Iterator, Optional

from uniseg import Unicode_Property
from uniseg.breaking import (Breakable, Breakables, Run, TailorFunc,
                             boundaries, break_units)
from uniseg.db import get_column_index, get_value
from uniseg.derived import InCB, indic_conjunct_break
from uniseg.emoji import extended_pictographic

__all__ = [
    'Grapheme_Cluster_Break',
    'GCB',
    'grapheme_cluster_break',
    'grapheme_cluster_breakables',
    'grapheme_cluster_boundaries',
    'grapheme_clusters',
]

INDEX_GRAPHEME_CLUSTER_BREAK = get_column_index('Grapheme_Cluster_Break')


class Grapheme_Cluster_Break(Unicode_Property):
    """Grapheme_Cluster_Break property values in UAX #29."""
    Other = 'Other'
    """Grapheme_Cluster_Break property value Other"""
    CR = 'CR'
    """Grapheme_Cluster_Break property value CR"""
    LF = 'LF'
    """Grapheme_Cluster_Break property value LF"""
    Control = 'Control'
    """Grapheme_Cluster_Break property value Control"""
    Extend = 'Extend'
    """Grapheme_Cluster_Break property value Extend"""
    ZWJ = 'ZWJ'
    """Grapheme_Cluster_Break property value ZWJ"""
    Regional_Indicator = 'Regional_Indicator'
    """Grapheme_Cluster_Break property value Regional_Indicator"""
    Prepend = 'Prepend'
    """Grapheme_Cluster_Break property value Prepend"""
    SpacingMark = 'SpacingMark'
    """Grapheme_Cluster_Break property value SpacingMark"""
    L = 'L'
    """Grapheme_Cluster_Break property value L"""
    V = 'V'
    """Grapheme_Cluster_Break property value V"""
    T = 'T'
    """Grapheme_Cluster_Break property value T"""
    LV = 'LV'
    """Grapheme_Cluster_Break property value LV"""
    LVT = 'LVT'
    """Grapheme_Cluster_Break property value LVT"""


# type alias for `GraphemeClusterBreak`
GCB = Grapheme_Cluster_Break


def _ep(ch: Optional[str], /) -> Optional[bool]:
    return False if ch is None else extended_pictographic(ch)


def grapheme_cluster_break(ch: str, index: int = 0, /) -> Grapheme_Cluster_Break:
    r"""Return the Grapheme_Cluster_Break property of `ch`.

    `ch` must be a single Unicode string.

    >>> grapheme_cluster_break('a')
    Grapheme_Cluster_Break.Other
    >>> grapheme_cluster_break('\x0d')
    Grapheme_Cluster_Break.CR
    >>> print(grapheme_cluster_break('\x0a'))
    LF

    If `index` is specified, this function consider `c` as a unicode
    string and return Grapheme_Cluster_Break property of the code
    point at ``c[index]``.

    >>> grapheme_cluster_break('a\x0d', 1).name
    'CR'
    """
    return Grapheme_Cluster_Break[
        get_value(ord(ch[index]), INDEX_GRAPHEME_CLUSTER_BREAK) or 'Other'
    ]


def grapheme_cluster_breakables(s: str, /) -> Breakables:
    """Iterate grapheme cluster breaking opportunities for every
    position of `s`.

    1 for "break" and 0 for "do not break".  The length of iteration
    will be the same as ``len(s)``.

    >>> list(grapheme_cluster_breakables('ABC'))
    [1, 1, 1]
    >>> list(grapheme_cluster_breakables('\x67\u0308'))
    [1, 0]
    >>> list(grapheme_cluster_breakables(''))
    []
    """
    if not s:
        return iter([])

    run = Run(s, indic_conjunct_break)
    while run.walk():
        if (
            run.is_following((InCB.Extend, InCB.Linker),
                             greedy=True).prev == InCB.Consonant
            and run.is_following(InCB.Extend, greedy=True).prev != InCB.Consonant
            and run.curr == InCB.Consonant
        ):
            run.do_not_break_here()
    incb_breakables = run.breakables()

    run = Run(s, grapheme_cluster_break)
    while run.walk():
        # GB3
        if run.prev == GCB.CR and run.curr == GCB.LF:
            run.do_not_break_here()
        # GB4, GB5
        elif (
            run.prev in (GCB.Control, GCB.CR, GCB.LF)
            or run.curr in (GCB.Control, GCB.CR, GCB.LF)
        ):
            run.break_here()
        # GB6, GB7, GB8
        elif (
            (run.prev == GCB.L and run.curr in (GCB.L, GCB.V, GCB.LV, GCB.LVT))
            or (run.prev in (GCB.LV, GCB.V) and run.curr in (GCB.V, GCB.T))
            or (run.prev in (GCB.LVT, GCB.T) and run.curr == GCB.T)
        ):
            run.do_not_break_here()
        elif run.curr in (GCB.Extend, GCB.ZWJ):
            run.do_not_break_here()
        # GB9a, GB9b
        elif (
            run.curr == GCB.SpacingMark
            or run.prev == GCB.Prepend
        ):
            run.do_not_break_here()
        # GB9c
        elif incb_breakables[run.position] is Breakable.DoNotBreak:
            run.do_not_break_here()
        # GB11
        elif (
            _ep(run.is_following(GCB.ZWJ).is_following(
                GCB.Extend, greedy=True).pc)
            and _ep(run.cc)
        ):
            run.do_not_break_here()
    # GB12, GB13
    run.head()
    while 1:
        while run.curr != GCB.Regional_Indicator:
            if not run.walk():
                break
        if not run.walk():
            break
        while run.prev == run.curr == GCB.Regional_Indicator:
            run.do_not_break_here()
            if not run.walk():
                break
            if not run.walk():
                break
    run.set_default(Breakable.Break)
    return run.literal_breakables()


def grapheme_cluster_boundaries(
        s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[int]:
    """Iterate indices of the grapheme cluster boundaries of `s`.

    This function yields from 0 to the end of the string (== len(s)).

    >>> list(grapheme_cluster_boundaries('ABC'))
    [0, 1, 2, 3]
    >>> list(grapheme_cluster_boundaries('\x67\u0308'))
    [0, 2]
    >>> list(grapheme_cluster_boundaries(''))
    []
    """
    breakables = grapheme_cluster_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def grapheme_clusters(
        s: str, tailor: Optional[TailorFunc] = None, /) -> Iterator[str]:
    r"""Iterate every grapheme cluster token of `s`.

    Grapheme clusters (both legacy and extended):

    >>> list(grapheme_clusters('g\u0308')) == ['g\u0308']
    True
    >>> list(grapheme_clusters('\uac01')) == ['\uac01']
    True
    >>> list(grapheme_clusters('\u1100\u1161\u11a8')) == ['\u1100\u1161\u11a8']
    True

    Extended grapheme clusters:

    >>> list(grapheme_clusters('\u0ba8\u0bbf')) == ['\u0ba8\u0bbf']
    True
    >>> list(grapheme_clusters('\u0937\u093f')) == ['\u0937\u093f']
    True

    Empty string leads the result of empty sequence:

    >>> list(grapheme_clusters('')) == []
    True

    You can customize the default breaking behavior by modifying
    breakable table so as to fit the specific locale in `tailor`
    function.  It receives `s` and its default breaking sequence
    (iterator) as its arguments and returns the sequence of customized
    breaking opportunities:

    >>> def tailor_grapheme_cluster_breakables(s, breakables):
    ...
    ...     for i, breakable in enumerate(breakables):
    ...         # don't break between 'c' and 'h'
    ...         if s.endswith('c', 0, i) and s.startswith('h', i):
    ...             yield 0
    ...         else:
    ...             yield breakable
    ...
    >>> s = 'Czech'
    >>> list(grapheme_clusters(s)) == ['C', 'z', 'e', 'c', 'h']
    True
    >>> list(grapheme_clusters(
    ...     s, tailor_grapheme_cluster_breakables)) == ['C', 'z', 'e', 'ch']
    True
    """
    breakables = grapheme_cluster_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
