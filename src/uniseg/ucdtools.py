"""Utility tools for Unicode Character Database files.

The UCD files are published under <https://www.unicode.org/Public/>.
"""

import re
from typing import Iterable, Iterator, Optional, TextIO, Union, overload

RX_CODE_POINT_RANGE_LITERAL = re.compile(
    r'(?P<cp1>[0-9A-Fa-f]{4,5})(?:\.\.(?P<cp2>[0-9A-Fa-f]{4,5}))?'
)


class CodePointSpan(object):
    """a class which represents a certain range of code points."""

    __slots__ = ['_start', '_end']

    @overload
    def __init__(self, arg1: str, /) -> None:
        """`arg1` is a literal string with two hexadeciam code points.
        e.g. '0600..0605'

        >>> r = CodePointSpan('0600..0605')
        >>> r = CodePointSpan('06DD')
        """
        ...

    @overload
    def __init__(self, arg1: int, arg2: Optional[int] = None, /) -> None:
        """`arg1` is the first code point integer of the range, and `arg2` is
        the last code point interger of that.  Specify `None` if the intance
        represents only one single codepoint.]

        >>> span = CodePointSpan(0x0600, 0x0605)
        >>> span = CodePointSpan(0x06dd)
        >>> span = CodePointSpan(0x06dd, None)
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
        self._start = arg1
        self._end = arg2 or arg1

    @property
    def start(self) -> int:
        """The first code point interger of the range.

        >>> span = CodePointSpan('0600..0605')
        >>> span.start
        1536
        >>> span = CodePointSpan(0x06dd)
        >>> span.start
        1757
        """
        return self._start

    @property
    def end(self) -> int:
        """The last code point interger of the range.

        If the instance represents a sigle code point, it returns the save
        integer value as the `start` property.

        >>> span = CodePointSpan('0600..0605')
        >>> span.end
        1541
        >>> span = CodePointSpan(0x06dd)
        >>> span.end
        1757
        """
        return self._end

    def __iter__(self) -> Iterator[int]:
        """Iterate every single code point of the range."""
        if self.end is None:
            yield self.start
        else:
            yield from range(self.start, self.end + 1)

    def __len__(self) -> int:
        """Return the number of the code points which the instance represents.

        >>> span = CodePointSpan('0600..0605')
        >>> len(span)
        6
        >>> span = CodePointSpan(0x06dd)
        >>> len(span)
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

        >>> span = CodePointSpan('0600..0605')
        >>> span.re()
        '\\u0600-\\u0605'
        >>> span = CodePointSpan(0x06dd)
        >>> span.re()
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


def code_point_literal(code_point: int) -> str:
    r"""return str literal expression for the code point.

    >>> code_point_literal(0x0030)
    '\\u0030'
    >>> code_point_literal(0x10030)
    '\\U00010030'
    """
    if code_point < 0x10000:
        return f'\\u{code_point:04x}'
    else:
        return f'\\U{code_point:08x}'


def split_comment(line: str) -> tuple[str, str]:
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


def iter_records(stream: TextIO) -> Iterable[tuple[str, ...]]:
    """iterate tuples of tokens on the text data (comments are removed)."""
    for raw_line in stream:
        # strip comment
        line = raw_line[:i if (i := raw_line.find('#')) >= 0 else None].strip()
        if line:
            fields = tuple(x.strip() for x in line.split(';'))
            yield fields


def group_continuous(iterable: Iterable[int]) -> Iterator[Iterable[int]]:
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
