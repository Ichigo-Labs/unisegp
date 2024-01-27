"""uniseg database lookup interface. """

from typing import List

from uniseg import db_lookups
from uniseg.codepoint import ord


def _find_break(u: str, /) -> int:
    """
    find code code point in hashmap
    """
    code = ord(u)
    if code >= 0x110000:
        return 0
    else:
        index = db_lookups.index1[code >> db_lookups.shift]
        return db_lookups.index2[
            (index << db_lookups.shift) + (code & ((1 << db_lookups.shift) - 1))
        ]

def grapheme_cluster_break(u: str, /) -> str:
    return db_lookups.grapheme_cluster_break_list[_find_break(u)]


def word_break(u: str, /) -> str:
    return db_lookups.word_break_list[_find_break(u)]


def sentence_break(u: str, /) -> str:
    return db_lookups.sentence_break_list[_find_break(u)]


def line_break(u: str, /) -> str:
    return db_lookups.line_break_list[_find_break(u)]
