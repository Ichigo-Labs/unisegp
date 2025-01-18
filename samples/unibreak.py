#!/usr/bin/env python3
"""unibreak.py - show Unicode segmentation breaks.

A sample script for uniseg package.

This work is marked with CC0 1.0
https://creativecommons.org/publicdomain/zero/1.0/

The uniseg package is licensed under the MIT License.
https://uniseg-py.readthedocs.io/
"""


from argparse import ArgumentParser, FileType
from typing import Callable, Iterator, TextIO

from uniseg.graphemecluster import grapheme_clusters
from uniseg.linebreak import line_break_units
from uniseg.sentencebreak import sentences
from uniseg.wordbreak import words


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument(
        '--mode', '-m',
        default='w',
        choices='gwsl',
        help="""breaking algorithm (default: %(default)s)
            g: grapheme clusters
            w: words
            s: sentences
            l: line breaking units
        """
    )
    parser.add_argument(
        'file',
        default='-',
        type=FileType(encoding='utf-8'),
        help="""input text file. '-' for stdin."""
    )
    args = parser.parse_args()

    output: TextIO = args.file
    seg_func: Callable[[str], Iterator[str]] = {
        'g': grapheme_clusters,
        'l': line_break_units,
        's': sentences,
        'w': words
    }[args.mode]
    for line in output:
        for segment in seg_func(line):
            print(repr(segment))


if __name__ == '__main__':
    main()
