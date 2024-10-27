"""Breakable table and string tokenization."""

from collections.abc import Callable, Iterable, Iterator, Sequence
from copy import copy
from enum import Enum
from typing import Generic, Literal, Optional, TypeVar

__all__ = [
    'Breakable',
    'Breakables',
    'TailorFunc',
    'Run',
    'boundaries',
    'break_units',
]


class Breakable(Enum):
    DoNotBreak = 0
    Break = 1

    def __bool__(self) -> bool:
        return bool(self.value)


# type aliases for annotation
Breakables = Iterable[Literal[0, 1]]
TailorFunc = Callable[[str, Breakables], Breakables]


T = TypeVar('T')


class Run(Generic[T]):
    """A utitlity class which helps treating break determination for a string."""

    def __init__(self, text: str, func: Callable[[str], T] = lambda x: x, /):
        """Utitlity class which helps treating break determination for a string.

        `text`
            string to determine breakable information.
        `func`
            property function to get a specific value for each character
            (code page) of the string.
        """
        self._text = text
        self._values = [func(c) for c in text]
        self._skip = tuple[str, ...]()
        self._breakables = list[Optional[Breakable]](None for __ in text)
        self._position = 0
        self._condition = bool(text)

    def __bool__(self) -> bool:
        """Evaluate the instance itself represents if its context is valid.

        >>> bool(Run('a'))
        True
        >>> bool(Run(''))
        False
        >>> bool(Run('abc').is_leading('b'))
        True
        >>> bool(Run('abc').is_leading('b').is_leading('c'))
        True
        >>> bool(Run('abc').is_leading('x'))
        False
        >>> bool(Run('abc').is_leading('b').is_leading('c'))
        True
        >>> bool(Run('abc').is_leading('x').is_leading('c'))
        False
        """
        return self._condition

    @property
    def position(self) -> int:
        """Current index position."""
        return self._position

    @property
    def text(self) -> str:
        """Initial string.

        >>> Run('abc').text
        'abc'
        """
        return self._text

    @property
    def curr(self) -> Optional[T]:
        """Property value for the current position, or None if it is invalid."""
        return self.value()

    @property
    def prev(self) -> Optional[T]:
        """Property value for the previous position, or None if it is invalid."""
        return self.value(-1)

    @property
    def next(self) -> Optional[T]:
        """Property value for the next position, or None if it is invalid."""
        return self.value(1)

    @property
    def breakables(self) -> list[Optional[Breakable]]:
        return self._breakables

    @property
    def chr(self) -> str:
        return self._text[self._position]

    def _calc_position(self, offset: int, /, noskip: bool = False) -> int:
        i = self._position
        vec = offset // abs(offset) if offset else 0
        for __ in range(abs(offset)):
            i += vec
            while 0 <= i < len(self._text) and (not noskip and self._values[i] in self._skip):
                i += vec
        return i

    def value(self, offset: int = 0, /, noskip: bool = False) -> Optional[T]:
        """Return value at current position + offset.

        >>> run = Run('abc', lambda x: x.upper())
        >>> run.value(1)
        'B'
        >>> run.value(2)
        'C'
        >>> run.walk()
        True
        >>> run.value(-1)
        'A'
        >>> run.head()
        >>> run.skip('B')
        >>> run.value(1)
        'C'
        >>> run.value(1, noskip=True)
        'B'
        """
        i = self._calc_position(offset, noskip=noskip)
        if self._condition and 0 <= i < len(self._text):
            return self._values[i]
        else:
            return None

    def values(self) -> list[T]:
        """Return a copy of the list of its properties."""
        return self._values[:]

    def walk(self, offset: int = 1, /, noskip: bool = False) -> bool:
        if self._condition:
            pos = self._calc_position(offset, noskip=noskip)
            condition = False
            if pos < 0:
                pos = 0
            elif len(self._text) <= pos:
                pos = len(self._text) - 1
            else:
                condition = True
            self._position = pos
            self._condition = condition
        return self._condition

    def head(self) -> None:
        self._position = 0
        self._condition = True

    def skip(self, values: Sequence[T]) -> None:
        self._skip = tuple(values)

    def is_continuing(
        self,
        values: Sequence[T],
        /,
        variable: bool = False,
        backward: bool = False,
        noskip: bool = False,
    ) -> 'Run[T]':
        """Test if values appears before / after the current position.

        Return shallow copy of the instance which position is at the end of
        the tested continuing series.

        >>> run = Run('abc', lambda x: x.upper())
        >>> run.is_continuing('B').curr
        'B'
        >>> run.is_continuing('B').next
        'C'
        >>> run.is_continuing('X', variable=True).curr
        'A'
        >>> run.is_continuing('X', variable=True).next
        'B'
        >>> bool(run.is_continuing('B').is_continuing('C'))
        True
        >>> run.walk()
        True
        >>> run.is_continuing('B').curr is None
        True
        >>> run.is_continuing('A', backward=True).curr
        'A'

        >>> run = Run('abbbccd', lambda x: x.upper())
        >>> run.is_continuing('B', variable=True).curr
        'B'
        >>> run.skip(('C',))
        >>> run.is_continuing('B', variable=True).next
        'D'
        >>> run.is_continuing('B', variable=True).value(1, noskip=True)
        'C'

        >>> run = Run('abbbccd', lambda x: x.upper())
        >>> run.walk(4)
        True
        >>> run.curr
        'C'
        >>> run.is_continuing('B', variable=True, backward=True).prev
        'A'
        """
        run = copy(self)
        vec = -1 if backward else 1
        if variable:
            while run.value(vec, noskip=noskip) in values:
                if not run.walk(vec, noskip=noskip):
                    break
            condition = True
        else:
            condition = run.walk(vec, noskip=noskip) and run.curr in values
        run._condition = self._condition and condition
        return run

    def is_following(
        self, values: Sequence[T], /, variable: bool = False, noskip: bool = False
    ) -> 'Run[T]':
        return self.is_continuing(values, variable=variable, backward=True, noskip=noskip)

    def is_leading(
        self, values: Sequence[T], /, variable: bool = False, noskip: bool = False
    ) -> 'Run[T]':
        return self.is_continuing(values, variable=variable, noskip=noskip)

    def break_here(self) -> None:
        if self._text and self._breakables[self._position] is None:
            self._breakables[self._position] = Breakable.Break

    def do_not_break_here(self) -> None:
        if self._text and self._breakables[self._position] is None:
            self._breakables[self._position] = Breakable.DoNotBreak

    def does_break_here(self) -> bool:
        return bool(self._breakables[self._position])

    def set_default(self, breakable: Breakable) -> None:
        self._breakables[:] = [
            breakable if x is None else x for x in self._breakables
        ]

    def literal_breakables(
            self, default: Breakable = Breakable.Break
    ) -> Iterable[Literal[0, 1]]:
        return (default.value if x is None else x.value for x in self._breakables)


def boundaries(breakables: Breakables, /) -> Iterator[int]:
    """Iterate boundary indices of the breakabe table, `breakables`.

    The boundaries start from 0 to the end of the sequence (==
    len(breakables)).

    >>> list(boundaries([1, 1, 1]))
    [0, 1, 2, 3]
    >>> list(boundaries([1, 0, 1]))
    [0, 2, 3]
    >>> list(boundaries([0, 1, 0]))
    [1, 3]

    It yields empty when the given sequece is empty.

    >>> list(boundaries([]))
    []
    """
    i = None
    for i, breakable in enumerate(breakables):
        if breakable:
            yield i
    if i is not None:
        yield i+1


def break_units(s: str, breakables: Breakables, /) -> Iterator[str]:
    """Iterate every tokens of `s` basing on breakable table, `breakables`.

    >>> list(break_units('ABC', [1, 1, 1])) == ['A', 'B', 'C']
    True
    >>> list(break_units('ABC', [1, 0, 1])) == ['AB', 'C']
    True
    >>> list(break_units('ABC', [1, 0, 0])) == ['ABC']
    True

    The length of `s` must be equal to that of `breakables`.
    """
    i = 0
    for j, bk in enumerate(breakables):
        if bk:
            if j:
                yield s[i:j]
            i = j
    if s:
        yield s[i:]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
