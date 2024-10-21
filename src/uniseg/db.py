"""uniseg database lookup interface. """

from sys import maxunicode

from uniseg.codepoint import ord
from uniseg.db_lookups import (grapheme_cluster_break_list, index1, index2,
                               line_break_list, sentence_break_list, shift,
                               word_break_list)


def _find_break(ch: str, /) -> int:
    """Find code point in hashmap."""
    cp = ord(ch)
    if maxunicode < cp:
        return 0
    else:
        index = index1[cp >> shift]
        return index2[(index << shift) + (cp & ((1 << shift) - 1))]


def grapheme_cluster_break(ch: str, /) -> str:
    return grapheme_cluster_break_list[_find_break(ch)]


def word_break(ch: str, /) -> str:
    return word_break_list[_find_break(ch)]


def sentence_break(ch: str, /) -> str:
    return sentence_break_list[_find_break(ch)]


def line_break(ch: str, /) -> str:
    return line_break_list[_find_break(ch)]
