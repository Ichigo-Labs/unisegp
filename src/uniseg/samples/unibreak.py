#!/usr/bin/env python3
"""unibreak.py - show Unicode segmentation breaks.

A sample script for uniseg package.

This work is marked with CC0 1.0
https://creativecommons.org/publicdomain/zero/1.0/

The uniseg package is licensed under the MIT License.
https://uniseg-py.readthedocs.io/
"""


from typing import Callable, Iterator, TextIO
from argparse import ArgumentParser, FileType

from uniseg.codepoint import code_points
from uniseg.graphemecluster import grapheme_clusters
from uniseg.linebreak import line_break_units
from uniseg.sentencebreak import sentences
from uniseg.wordbreak import words


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument(
        '-m', '--mode',
        default='w',
        choices=['c', 'g', 'l', 's', 'w'],
        help="""breaking algorithm (c: code points, g: grapheme clusters,
        s: sentences l: line breaking units, w: words) default: %(default)s"""
    )
    parser.add_argument(
        'file',
        default='-',
        type=FileType(),
        help="""input text file. '-' for stdin. """
    )
    args = parser.parse_args()

    fin: TextIO = args.file
    seg_func :Callable[[str], Iterator[str]] = {
        'c': code_points,
        'g': grapheme_clusters,
        'l': line_break_units,
        's': sentences,
        'w': words
    }[args.mode]
    for line in fin:
        for segment in seg_func(line):
            print(repr(segment))


if __name__ == '__main__':
    main()
