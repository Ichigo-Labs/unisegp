#!/usr/bin/env python3
"""Extract UCD properties in CSV format."""

import csv
from argparse import ArgumentParser, FileType

from uniseg.ucdtools import CodePointSpan, iter_records


def main() -> None:
    """Main entry point."""

    parser = ArgumentParser()
    parser.add_argument('-o', '--output', default='-',
                        type=FileType('w', encoding='utf-8'))
    parser.add_argument('file',
                        type=FileType('r', encoding='utf-8'),
                        help='UCD test file')
    args = parser.parse_args()

    rows = []
    for record in iter_records(args.file):
        fields, __ = record
        if len(fields) > 1:
            span = CodePointSpan(fields[0])
            props = fields[1:]
            for cp in span:
                rows.append((cp,) + props)
    rows.sort()
    writer = csv.writer(args.output)
    writer.writerows(rows)


if __name__ == '__main__':
    main()
