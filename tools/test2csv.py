#!/usr/bin/env python3
"""Extract UCD test cases in CSV format."""


import re
from argparse import ArgumentParser, FileType
from typing import TextIO, Union


def csv_escape(value: Union[int, str]) -> str:
    '''Return escaped string suitable as a CSV field.

    >>> csv_escape(1)
    '1'
    >>> csv_escape('hello')
    'hello'
    >>> csv_escape(',')
    '","'
    >>> csv_escape('"hi"')
    '"""hi"""'
    '''

    s = '%s' % value
    if re.search(r'[,"\n]', s):
        s = '"%s"' % s.replace('"', '""')
    return s


def split_comment(line: str) -> tuple[str, str]:
    """Split a line into a data part and a comment.

    >>> split_comment('data # comment')
    ('data', 'comment')
    >>> split_comment('data')
    ('data', '')
    """

    if '#' in line:
        data, comment = line.split('#', 1)
    else:
        data = line
        comment = ''
    return data.strip(), comment.strip()


def main() -> None:
    """Main entry point."""

    parser = ArgumentParser()
    parser.add_argument('-o', '--output', default='-',
                        type=FileType('w', encoding='utf-8'))
    parser.add_argument('-p', '--prefix', default='TEST')
    parser.add_argument('-t', '--testmod', action='store_true',
                        help='do doctest.testmod() and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose mode in testmod')
    parser.add_argument('file', nargs='?', default='-',
                        type=FileType('r', encoding='utf-8'),
                        help='UCD test file (default: stdin)')
    args = parser.parse_args()

    if args.testmod:
        import doctest
        doctest.testmod(verbose=args.verbose)
        exit()

    input: TextIO = args.file
    output: TextIO = args.output
    name_prefix: str = args.prefix
    test_num = 1
    for line in input:
        data, comment = split_comment(line)
        if not data:
            continue
        name = '%s%04d' % (name_prefix, test_num)
        fields = [name, data, comment]
        print(','.join(csv_escape(x) for x in fields), file=output)
        test_num += 1


if __name__ == '__main__':
    main()
