#!/usr/bin/env python3
"""uniwrap.py - wrap text using Unicode segmentation breaks.

A sample script for uniseg package.

This work is marked with CC0 1.0
https://creativecommons.org/publicdomain/zero/1.0/

The uniseg package is licensed under the MIT License.
https://uniseg-py.readthedocs.io/
"""

from argparse import ArgumentParser, FileType
from typing import TextIO

from uniseg.wrap import tt_wrap


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument( '-r', '--ruler', action='store_true',
                        help='show ruler')
    parser.add_argument('-t', '--tab-width', type=int, default=8,
                        help='tab width (%(default)d)')
    parser.add_argument('-l', '--legacy', action='store_true',
                        help='treat ambiguous-width letters as wide')
    parser.add_argument('-o', '--output', default='-', type=FileType('w'),
                        help='leave output to specified file')
    parser.add_argument('-w', '--wrap-width', type=int, default=60,
                        help='wrap width (%(default)s)')
    parser.add_argument('-c', '--char-wrap', action='store_true',
                        help="""wrap on grapheme boundaries instead of line
                        break boundaries""")
    parser.add_argument('file', default='-', type=FileType(),
                        help='input file')
    args = parser.parse_args()

    ruler: bool = args.ruler
    tab_width: int = args.tab_width
    wrap_width: int = args.wrap_width
    char_wrap: bool = args.char_wrap
    legacy: bool = args.legacy
    fin: TextIO = args.file
    fout: TextIO = args.output

    if ruler:
        if tab_width > 0:
            ruler_text = (('+' + '-' * (tab_width - 1))
                          * (wrap_width // tab_width + 1))[:wrap_width]
        else:
            ruler_text = '-' * wrap_width
        print(ruler_text, file=fout)

    for para in fin:
        for line in tt_wrap(para, wrap_width, tab_width=tab_width,
                            ambiguous_as_wide=legacy, char_wrap=char_wrap):
            print(line, file=fout)


if __name__ == '__main__':
    main()
