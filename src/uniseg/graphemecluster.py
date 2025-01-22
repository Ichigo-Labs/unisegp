"""Unicode grapheme cluster boundaries.

`UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
<https://www.unicode.org/reports/tr29/tr29-45.html>`_
"""

from typing import Iterator, Optional

from uniseg import Unicode_Property
from uniseg.breaking import (Breakable, Breakables, Run, TailorBreakables, boundaries,
                             break_units)
from uniseg.db import get_handle, get_value
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


H_GRAPHEME_CLUSTER_BREAK = get_handle('Grapheme_Cluster_Break')


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


def _ep(c: Optional[str], /) -> Optional[bool]:
    return False if c is None else extended_pictographic(c)


def grapheme_cluster_break(c: str, /) -> Grapheme_Cluster_Break:
    R"""Return the Grapheme_Cluster_Break property of `c`.

    `c` must be a single Unicode string.

    >>> grapheme_cluster_break('a')
    Grapheme_Cluster_Break.Other
    >>> grapheme_cluster_break('\r')
    Grapheme_Cluster_Break.CR
    >>> print(grapheme_cluster_break('\n'))
    LF
    """
    return Grapheme_Cluster_Break[
        get_value(H_GRAPHEME_CLUSTER_BREAK, ord(c)) or 'Other'
    ]


def grapheme_cluster_breakables(s: str, /) -> Breakables:
    R"""Iterate grapheme cluster breaking opportunities for every
    position of `s`.

    1 for "break" and 0 for "do not break".  The length of iteration
    will be the same as ``len(s)``.

    >>> list(grapheme_cluster_breakables('ABC'))
    [1, 1, 1]
    >>> list(grapheme_cluster_breakables('g̈')) # (== '\u0067\u0308')
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
        elif run.curr == GCB.SpacingMark or run.prev == GCB.Prepend:
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
    s: str, /, tailor: Optional[TailorBreakables] = None
) -> Iterator[int]:
    R"""Iterate indices of the grapheme cluster boundaries of `s`.

    This function yields from 0 to the end of the string (== len(s)).

    >>> list(grapheme_cluster_boundaries('ABC'))
    [0, 1, 2, 3]
    >>> list(grapheme_cluster_boundaries('g̈')) # (== '\u0067\u0308')
    [0, 2]
    >>> list(grapheme_cluster_boundaries(''))
    []
    """
    breakables = grapheme_cluster_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return boundaries(breakables)


def grapheme_clusters(
    s: str, /, tailor: Optional[TailorBreakables] = None
) -> Iterator[str]:
    R"""Iterate every grapheme cluster token of `s`.

    Grapheme clusters (both legacy and extended):

    >>> list(grapheme_clusters('g̈')) # (== '\u0067\u0308')
    ['g̈']
    >>> list(grapheme_clusters('각')) # (== '\uac01')
    ['각']
    >>> list(grapheme_clusters('각')) # (== '\u1100\u1161\u11a8')
    ['각']

    Extended grapheme clusters:

    >>> list(grapheme_clusters('நி')) # (== '\u0ba8\u0bbf')
    ['நி']
    >>> list(grapheme_clusters('षि')) # (== '\u0937\u093f')
    ['षि']

    Empty string leads the result of empty sequence:

    >>> list(grapheme_clusters(''))
    []

    You can customize the default breaking behavior by modifying breakable
    table so as to fit the specific locale in `tailor` function.  It receives
    `s` and its default breaking sequence (iterator) as its arguments and
    returns the sequence of customized breaking opportunities:

    >>> def tailor_grapheme_cluster_breakables(s, breakables):
    ...     for i, breakable in enumerate(breakables):
    ...         # don't break between 'c' and 'h'
    ...         if s.endswith('c', 0, i) and s.startswith('h', i):
    ...             yield 0
    ...         else:
    ...             yield breakable
    ...
    >>> list(grapheme_clusters('Czech'))
    ['C', 'z', 'e', 'c', 'h']
    >>> list(grapheme_clusters('Czech', tailor_grapheme_cluster_breakables))
    ['C', 'z', 'e', 'ch']
    """
    breakables = grapheme_cluster_breakables(s)
    if tailor is not None:
        breakables = tailor(s, breakables)
    return break_units(s, breakables)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
