"""Utility tools for Unicode Character Database files.

The UCD files are published under <https://www.unicode.org/Public/>.
"""

import re
from dataclasses import dataclass
from typing import (Iterable, Iterator, NamedTuple, Optional, TextIO, Union,
                    overload)

RX_CODE_POINT_RANGE_LITERAL = re.compile(
    r'(?P<cp1>[0-9A-Fa-f]{4,5})(?:\.\.(?P<cp2>[0-9A-Fa-f]{4,5}))?'
)


@dataclass(init=False, repr=False, order=True)
class CodePointSpan:
    """A data class which represents a certain range of code points."""
    start: int
    end: int

    @overload
    def __init__(self, arg1: str, /) -> None:
        """`arg1` is a literal string with two hexadeciam code points.
        e.g. '0600..0605'

        >>> CodePointSpan('0600..0605')
        <CodePointSpan [0600..0605]>
        >>> CodePointSpan('06DD')
        <CodePointSpan [06DD]>
        """
        ...

    @overload
    def __init__(self, arg1: int, arg2: Optional[int] = None, /) -> None:
        """`arg1` is the first code point integer of the range, and `arg2` is
        the last code point interger of that.  Specify `None` if the intance
        represents only one single codepoint.]

        >>> CodePointSpan(0x0600, 0x0605)
        <CodePointSpan [0600..0605]>
        >>> CodePointSpan(0x06dd)
        <CodePointSpan [06DD]>
        >>> CodePointSpan(0x06dd, None)
        <CodePointSpan [06DD]>
        """
        ...

    def __init__(self, arg1: Union[str, int], arg2: Optional[int] = None, /) -> None:
        if isinstance(arg1, str):
            m = RX_CODE_POINT_RANGE_LITERAL.match(arg1)
            if m is None:
                raise ValueError(f'invalid code point range leteral: {arg1!r}')
            arg1 = int(m.group('cp1'), 16)
            arg2 = int(_, 16) if (_ := m.group('cp2')) else None
        if arg2 is not None and arg2 <= arg1:
            raise ValueError('end is greater than start')
        self.start = arg1
        self.end = arg2 or arg1

    def __iter__(self) -> Iterator[int]:
        """Iterate every single code point of the range.

        >>> list(CodePointSpan(0x0600, 0x0605))
        [1536, 1537, 1538, 1539, 1540, 1541]
        """
        if self.end is None:
            yield self.start
        else:
            yield from range(self.start, self.end + 1)

    def __len__(self) -> int:
        """Return the number of the code points which the instance represents.

        >>> len(CodePointSpan('0600..0605'))
        6
        >>> len(CodePointSpan(0x06dd))
        1
        """
        return 1 if self.end is None else self.end - self.start + 1

    def __repr__(self) -> str:
        """Return `repr()` expression for the instance.

        >>> CodePointSpan('0600..0605')
        <CodePointSpan [0600..0605]>
        >>> CodePointSpan(0x06dd)
        <CodePointSpan [06DD]>
        """
        if self.start == self.end:
            s = f'{self.start:04X}'
        else:
            s = f'{self.start:04X}..{self.end:04X}'
        return f'<{__class__.__name__} [{s}]>'

    def re(self) -> str:
        R"""Return regeular expression string which represents the code point
        span.

        >>> CodePointSpan('0600..0605').re()
        '\\u0600-\\u0605'
        >>> CodePointSpan(0x06dd).re()
        '\\u06dd'
        """
        esc_start = code_point_literal(self.start)
        if self.start == self.end:
            return f'{esc_start}'
        else:
            esc_end = code_point_literal(self.end)
            if self.end - self.start == 1:
                return f'{esc_start}{esc_end}'
            else:
                return f'{esc_start}-{esc_end}'


class UcdRecord(NamedTuple):
    """A data class which represents fields and a comment of the UCD record.
    """
    fields: tuple[str, ...]
    comment: str


def code_point_literal(cp: int, /) -> str:
    R"""return str literal expression for the code point.

    >>> code_point_literal(0x0030)
    '\\u0030'
    >>> code_point_literal(0x10030)
    '\\U00010030'
    """
    if cp < 0x10000:
        return f'\\u{cp:04x}'
    else:
        return f'\\U{cp:08x}'


def split_comment(line: str, /) -> tuple[str, str]:
    """Split a string into two, a data part and a comment.

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


def iter_records(stream: TextIO, /) -> Iterable[UcdRecord]:
    """Iterate tuples of tokens on the text data (comments are removed)."""
    for line in stream:
        # strip comment
        field_part, comment_part = split_comment(line)
        if field_part:
            fields = tuple(x.strip() for x in field_part.split(';'))
            yield UcdRecord(fields, comment_part)


def iter_code_point_properties(stream: TextIO, /) -> Iterable[tuple[int, str]]:
    R"""Iterate tuples of code point interger and property string for every
    code point described in the UCD property text.

    >>> from io import StringIO
    >>> text = (
    ...     '002B          ; Math # Sm       PLUS SIGN\n'
    ...     '003C..003E    ; Math # Sm   [3] LESS-THAN SIGN..GREATER-THAN SIGN\n'
    ... )
    >>> stream = StringIO(text)
    >>> list(iter_code_point_properties(stream))
    [(43, 'Math'), (60, 'Math'), (61, 'Math'), (62, 'Math')]
    """
    for record in iter_records(stream):
        fields, __ = record
        if len(fields) > 1:
            span = CodePointSpan(fields[0])
            prop = fields[1]
            for cp in span:
                yield cp, prop


def group_continuous(iterable: Iterable[int], /) -> Iterator[Iterable[int]]:
    """iterate continuous `int` sequences in `iterable`.

    >>> L = [1, 2, 3, 10, 11, 21, 22, 23]
    >>> [list(x) for x in group_continuous(L)]
    [[1, 2, 3], [10, 11], [21, 22, 23]]
    >>> L = [1, 2, 3, 10, 11, 21]
    >>> [list(x) for x in group_continuous(L)]
    [[1, 2, 3], [10, 11], [21]]
    """
    start: Optional[int] = None
    prev: Optional[int] = None
    for i in iterable:
        if start is None:
            start = i
        if prev is not None and prev + 1 != i:
            yield range(start, prev+1)
            start = i
        prev = i
    if start is not None and prev is not None:
        yield range(start, prev+1)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
