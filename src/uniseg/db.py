from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)

from .codepoint import ord
from . import db_lookups

def _find_break(u):
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

def grapheme_cluster_break(u):
    return db_lookups.grapheme_cluster_break_list[_find_break(u)]


def iter_grapheme_cluster_break_tests():
    from . import db_lookups_test
    return db_lookups_test.grapheme_cluster_break_test


def word_break(u):
    return db_lookups.word_break_list[_find_break(u)]


def iter_word_break_tests():
    from . import db_lookups_test
    return db_lookups_test.word_break_test


def sentence_break(u):
    return db_lookups.sentence_break_list[_find_break(u)]


def iter_sentence_break_tests():
    from . import db_lookups_test
    return db_lookups_test.sentence_break_test


def line_break(u):
    return db_lookups.line_break_list[_find_break(u)]


def iter_line_break_tests():
    from . import db_lookups_test
    return db_lookups_test.line_break_test
