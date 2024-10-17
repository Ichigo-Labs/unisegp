import re
from typing import Iterable, Iterator, Optional, TextIO


RX_CODE_POINT_RANGE_LITERAL = re.compile(
    r'(?P<cp1>[0-9A-Fa-f]{4,5})(?:\.\.(?P<cp2>[0-9A-Fa-f]{4,5}))?')


class CodePointRange(object):

    __slots__ = ['_start', '_end']

    def __init__(self, start: int, end: Optional[int] = None):

        if end is not None and end <= start:
            raise ValueError('end is greater than start')

        self._start = start
        self._end = end

    @property
    def start(self) -> int:

        return self._start

    @property
    def end(self) -> Optional[int]:

        return self._end

    def __iter__(self) -> Iterator[int]:

        if self.end is None:
            yield self.start
        else:
            yield from range(self.start, self.end+1)

    def __len__(self) -> int:

        return 1 if self.end is None else self.end - self.start + 1

    def __repr__(self) -> str:

        if self.end is None:
            s = f'{self.start:04X}'
        else:
            s = f'{self.start:04X}..{self.end:04X}'
        return f'<{__class__.__name__} [{s}]>'

    def re_chars(self) -> str:

        esc_start = code_point_literal(self.start)
        if self.end is None:
            return f'{esc_start}'
        else:
            esc_end = code_point_literal(self.end)
            if self.end - self.start == 1:
                return f'{esc_start}{esc_end}'
            else:
                return f'{esc_start}-{esc_end}'

    @classmethod
    def from_literal(cls, s: str) -> 'CodePointRange':
        m = RX_CODE_POINT_RANGE_LITERAL.match(s)
        if m is None:
            raise ValueError(f'invalid code point range leteral: {s!r}')
        cp1 = int(m.group('cp1'), 16)
        cp2 = int(_, 16) if (_ := m.group('cp2')) else None
        return cls(cp1, cp2)


def code_point_literal(code_point: int) -> str:
    r"""return str literal expression for the code point

    >>> code_point_literal(0x0030)
    '\\u0030'
    >>> code_point_literal(0x10030)
    '\\U00010030'
    """

    if code_point < 0x10000:
        return f'\\u{code_point:04x}'
    else:
        return f'\\U{code_point:08x}'


def iter_records(f: TextIO) -> Iterable[tuple[str, ...]]:

    for raw_line in f:
        # strip comment
        line = raw_line[:i if (i := raw_line.find('#')) >= 0 else None].strip()
        if line:
            fields = tuple(x.strip() for x in line.split(';'))
            yield fields


def group_continuous(iterable: Iterable[int]) -> Iterator[Iterable[int]]:
    """Iterate continuous `int` sequences in `iterable`.

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
