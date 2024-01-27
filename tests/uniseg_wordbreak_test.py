#!/usr/bin/env python

import doctest
import unittest

from uniseg import wordbreak

from db_lookups_test import word_break_test
from uniseg_test import implement_break_tests


def iter_word_break_tests():
    return word_break_test


@implement_break_tests(wordbreak.word_boundaries,
                       iter_word_break_tests())
class WordBreakTest(unittest.TestCase):
    pass


def load_tests(loader, tests, ignore):

    tests.addTests(doctest.DocTestSuite(wordbreak))
    return tests


if __name__ == '__main__':
    unittest.main()
