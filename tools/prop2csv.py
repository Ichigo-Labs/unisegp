#!/usr/bin/env python3
"""Extract UCD properties in CSV format."""

import csv
from argparse import ArgumentParser, FileType

from uniseg.ucdtools import iter_code_point_properties


def main() -> None:
    """Main entry point."""

    parser = ArgumentParser()
    parser.add_argument('-o', '--output', default='-',
                        type=FileType('w', encoding='utf-8'))
    parser.add_argument('file',
                        type=FileType('r', encoding='utf-8'),
                        help='UCD test file')
    args = parser.parse_args()

    rows = sorted(iter_code_point_properties(args.file))
    writer = csv.writer(args.output)
    writer.writerows(rows)


if __name__ == '__main__':
    main()
