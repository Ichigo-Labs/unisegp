#!/usr/bin/env python

import doctest
import unittest

from uniseg import sentencebreak

from db_lookups_test import sentence_break_test
from uniseg_test import implement_break_tests


def iter_sentence_break_tests():
    return sentence_break_test


@implement_break_tests(sentencebreak.sentence_boundaries,
                       iter_sentence_break_tests())
class SentenceBreakTest(unittest.TestCase):
    pass


def load_tests(loader, tests, ignore):

    tests.addTests(doctest.DocTestSuite(sentencebreak))
    return tests


if __name__ == '__main__':
    unittest.main()
