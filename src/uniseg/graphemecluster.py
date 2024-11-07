"""Unicode grapheme cluster boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

from enum import Enum
from typing import Iterator, Optional

from uniseg.breaking import (Breakable, Breakables, Run, TailorFunc,
                             boundaries, break_units)
from uniseg.db import extended_pictographic
from uniseg.db import grapheme_cluster_break as _grapheme_cluster_break
from uniseg.db import indic_conjunct_break

__all__ = [
    'GraphemeClusterBreak',
    'GCB',
    'grapheme_cluster_break',
    'grapheme_cluster_breakables',
    'grapheme_cluster_boundaries',
    'grapheme_clusters',
]


class GraphemeClusterBreak(Enum):
    """Grapheme_Cluster_Break property values in UAX #29."""
    OTHER = 'Other'
    CR = 'CR'
    LF = 'LF'
    CONTROL = 'Control'
    EXTEND = 'Extend'
    ZWJ = 'ZWJ'
    REGIONAL_INDICATOR = 'Regional_Indicator'
    PREPEND = 'Prepend'
    SPACINGMARK = 'SpacingMark'
    L = 'L'
    V = 'V'
    T = 'T'
    LV = 'LV'
    LVT = 'LVT'


# type alias for `GraphemeClusterBreak`
GCB = GraphemeClusterBreak


def _ep(ch: Optional[str], /) -> Optional[bool]:
    return False if ch is None else extended_pictographic(ch)


def grapheme_cluster_break(ch: str, index: int = 0, /) -> GraphemeClusterBreak:
    r"""Return the Grapheme_Cluster_Break property of `ch`

    `ch` must be a single Unicode string.

    >>> grapheme_cluster_break('a')
    <GraphemeClusterBreak.OTHER: 'Other'>
    >>> grapheme_cluster_break('\x0d')
    <GraphemeClusterBreak.CR: 'CR'>
    >>> grapheme_cluster_break('\x0a').name
    'LF'

    If `index` is specified, this function consider `c` as a unicode
    string and return Grapheme_Cluster_Break property of the code
    point at c[index].

    >>> grapheme_cluster_break('a\x0d', 1).name
    'CR'
    """
    name = _grapheme_cluster_break(ch[index])
    return GraphemeClusterBreak[name.upper()]


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
            (
                run.is_following(('Extend', 'Linker'), greedy=True)
                .prev == 'Consonant'
                and run.is_following(('Extend',), greedy=True)
                .prev != 'Consonant'
            )
            and run.curr == 'Consonant'
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
            run.prev in (GCB.CONTROL, GCB.CR, GCB.LF)
            or run.curr in (GCB.CONTROL, GCB.CR, GCB.LF)
        ):
            run.break_here()
        # GB6, GB7, GB8
        elif (
            (run.prev == GCB.L and run.curr in (GCB.L, GCB.V, GCB.LV, GCB.LVT))
            or (run.prev in (GCB.LV, GCB.V) and run.curr in (GCB.V, GCB.T))
            or (run.prev in (GCB.LVT, GCB.T) and run.curr == GCB.T)
        ):
            run.do_not_break_here()
        elif run.curr in (GCB.EXTEND, GCB.ZWJ):
            run.do_not_break_here()
        # GB9a, GB9b
        elif (
            run.curr == GCB.SPACINGMARK
            or run.prev == GCB.PREPEND
        ):
            run.do_not_break_here()
        # GB9c
        elif incb_breakables[run.position] is Breakable.DoNotBreak:
            run.do_not_break_here()
        # GB11
        elif (
            _ep(run.is_following((GCB.ZWJ,)).is_following(
                (GCB.EXTEND,), greedy=True).pc)
            and _ep(run.cc)
        ):
            run.do_not_break_here()
    # GB12, GB13
    run.head()
    while 1:
        while run.curr != GCB.REGIONAL_INDICATOR:
            if not run.walk():
                break
        if not run.walk():
            break
        while run.prev == run.curr == GCB.REGIONAL_INDICATOR:
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
