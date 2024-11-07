#!/usr/bin/env python3
"""Generate uniseg break test code."""

import re
from argparse import ArgumentParser, FileType
from textwrap import wrap
from typing import NamedTuple, TextIO

from ucdtools import iter_records


class Entry(NamedTuple):
    """Data class for test record."""
    name: str       # 'XxxxBreakTestNNNN'
    pattern: str    # '÷ 0020 ÷ 0020 ÷'
    comment: str    # '÷ [0.2] SPACE (Other) ÷ [999.0] SPACE (Other) ÷ [0.3]


def parse_breaking_test_pattern(pattern: str) -> tuple[str, list[int]]:
    """Parse `pattern` and return test string and expected result."""

    BREAK = '\u00f7'
    DONT_BREAK = '\u00d7'
    codepoints: list[str] = []
    breakpoints: list[int] = []
    index = 0
    for token in pattern.split():
        if token == BREAK:
            breakpoints.append(index)
        elif token == DONT_BREAK:
            pass
        else:
            c = chr(int(token, 16))
            codepoints.append(c)
            index += len(c)
    return ''.join(codepoints), breakpoints


def generate_break_test_code(test: Entry, break_func_name: str) -> str:
    """Return test function code."""

    string, expect = parse_breaking_test_pattern(test.pattern)
    string_literal = string.encode('unicode_escape').decode(
        'ascii').replace("'", "\\'")
    doc_string = '\n'.join(wrap(
        test.pattern,
        76,
        initial_indent='       ',
        subsequent_indent='    '
    )).strip()
    doc_detail = '\n    '.join([
        f'{i}. {x}' for i, x in enumerate(
            re.findall(r'[\u00f7\u00d7][^\u00f7\u00d7]+', test.comment)
        )
    ])

    return (
        f'def test_{test.name.lower()}() -> None:\n'
        f'    """{doc_string}\n'
        f'\n'
        f'    {doc_detail}\n'
        f'    """\n'
        f'    actual = list({break_func_name}(\'{string_literal}\'))\n'
        f'    expect = {repr(expect)}\n'
        f'    assert expect == actual\n'
    )


def main() -> None:
    """Main entry point."""

    parser = ArgumentParser()
    parser.add_argument('-m', '--module', default='',
                        help='module name for importing break_func')
    parser.add_argument('-o', '--output', default='-',
                        type=FileType('w', encoding='utf-8'))
    parser.add_argument('break_func',
                        help='break function name')
    parser.add_argument('input', type=FileType('r', encoding='utf-8'),
                        help='UCD test file')
    args = parser.parse_args()

    module_name: str = args.module
    break_func: str = args.break_func
    input: TextIO = args.input
    output: TextIO = args.output

    codes: list[str] = [
        '#!/usr/bin/env python3\n'
        '# DO NOT EDIT.  This code is generated automatically.\n'
    ]

    if module_name:
        codes.append(f'from {module_name} import {break_func}\n')

    records = list(iter_records(input))
    digits = len(str(len(records)))
    for i, record in enumerate(records, 1):
        name = '_'.join([break_func, format(i, f'0{digits}d')])
        pattern = record.fields[0]
        comment = record.comment
        entry = Entry(name, pattern, comment)
        codes.append(generate_break_test_code(entry, break_func))

    codes.append(
        'if __name__ == "__main__":\n'
        '    import pytest\n'
        '    pytest.main([__file__])\n'
    )

    output.write('\n\n'.join(codes))


if __name__ == '__main__':
    main()
