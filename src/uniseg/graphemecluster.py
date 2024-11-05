"""Unicode grapheme cluster boundaries.

UAX #29: Unicode Text Segmentation (Unicode 16.0.0)
https://www.unicode.org/reports/tr29/tr29-45.html
"""

import re
from enum import Enum
from typing import Iterator, Optional

from uniseg.breaking import Breakables, TailorFunc, boundaries, break_units
from uniseg.db import grapheme_cluster_break as _grapheme_cluster_break
from uniseg.grapheme_re import PAT_EXTENDED_GRAPHEME_CLUSTER

__all__ = [
    'GraphemeClusterBreak',
    'GCB',
    'grapheme_cluster_break',
    'grapheme_cluster_breakables',
    'grapheme_cluster_boundaries',
    'grapheme_clusters',
]


_rx_grapheme = re.compile(PAT_EXTENDED_GRAPHEME_CLUSTER)


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
        return
    for graphem in _rx_grapheme.findall(s):
        yield 1
        for _ in range(len(graphem) - 1):
            yield 0


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
