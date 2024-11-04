"""uniseg database lookup interface. """

from sys import maxunicode

from uniseg.db_lookups import columns, index1, index2, shift, values

INDEX_GRAPHEME_CLUSTER_BREAK = columns.index('GraphemeClusterBreak')
INDEX_WORD_BREAK = columns.index('WordBreak')
INDEX_SENTENCE_BREAK = columns.index('SentenceBreak')
INDEX_LINE_BREAK = columns.index('LineBreak')
INDEX_EXTENDED_PICTOGRAPHIC = columns.index('Extended_Pictographic')
INDEX_INDIC_CONJUNCT_BREAK = columns.index('InCB')


def _find_break(ch: str, /) -> int:
    """Find code point in hashmap."""
    cp = ord(ch)
    if maxunicode < cp:
        return 0
    else:
        index = index1[cp >> shift]
        return index2[(index << shift) + (cp & ((1 << shift) - 1))]


def grapheme_cluster_break(ch: str, /) -> str:
    return values[_find_break(ch)][INDEX_GRAPHEME_CLUSTER_BREAK] or 'Other'


def word_break(ch: str, /) -> str:
    return values[_find_break(ch)][INDEX_WORD_BREAK] or 'Other'


def sentence_break(ch: str, /) -> str:
    return values[_find_break(ch)][INDEX_SENTENCE_BREAK] or 'Other'


def line_break(ch: str, /) -> str:
    return values[_find_break(ch)][INDEX_LINE_BREAK] or 'XX'


def extended_pictographic(ch: str, /) -> bool:
    return bool(values[_find_break(ch)][INDEX_EXTENDED_PICTOGRAPHIC])


def indic_conjunct_break(ch: str, /) -> bool:
    return bool(values[_find_break(ch)][INDEX_INDIC_CONJUNCT_BREAK])
