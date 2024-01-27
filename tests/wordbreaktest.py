#!/usr/bin/env python

import doctest
import unittest

from uniseg import wordbreak

from .test import iter_word_break_tests, implement_break_tests


@implement_break_tests(wordbreak.word_boundaries,
                       iter_word_break_tests())
class WordBreakTest(unittest.TestCase):
    pass


def load_tests(loader, tests, ignore):

    tests.addTests(doctest.DocTestSuite(wordbreak))
    return tests


if __name__ == '__main__':
    unittest.main()
