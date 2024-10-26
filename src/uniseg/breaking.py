"""Breakable table and string tokenization."""

from collections.abc import Callable, Iterable, Iterator, Sequence
from copy import copy
from enum import Enum
from typing import Generic, Literal, Optional, TypeVar

__all__ = [
    'Breakable',
    'Breakables',
    'TailorFunc',
    'Runner',
    'boundaries',
    'break_units',
]


class Breakable(Enum):
    Unknown = -1
    DoNotBreak = 0
    Break = 1

    def __bool__(self) -> bool:
        if self.value == Breakable.Unknown:
            raise ValueError(f'{self.value} is evaluated as bool')
        return bool(self.value)


# type aliases for annotation
Breakables = Iterable[Literal[0, 1]]
TailorFunc = Callable[[str, Breakables], Breakables]


T = TypeVar('T')


class Runner(Generic[T]):

    def __init__(self, text: str, func: Callable[[str], T]):
        self._text = text
        self._values = [func(c) for c in text]
        self._skip = tuple[str, ...]()
        self._breakables = [Breakable.Unknown for __ in text]
        self._position = 0
        self._condition = bool(text)

    def __bool__(self) -> bool:
        return self._condition

    @property
    def text(self) -> str:
        return self._text

    @property
    def values(self) -> list[T]:
        return self._values

    @property
    def breakables(self) -> list[Breakable]:
        return self._breakables

    @property
    def position(self) -> int:
        return self._position

    @property
    def curr(self) -> Optional[T]:
        return self.value()

    @property
    def prev(self) -> Optional[T]:
        return self.value(-1)

    @property
    def next(self) -> Optional[T]:
        return self.value(1)

    @property
    def chr(self) -> str:
        return self._text[self._position]

    def _calc_position(self, offset: int, /) -> int:
        i = self._position
        vec = offset // abs(offset) if offset else 0
        for __ in range(abs(offset)):
            i += vec
            while 0 <= i < len(self._text) and self._values[i] in self._skip:
                i += vec
        return i

    def value(self, offset: int = 0, /) -> Optional[T]:
        i = self._calc_position(offset)
        return self._values[i] if 0 <= i < len(self._text) else None

    def walk(self, offset: int = 1, /) -> bool:
        if self._condition:
            pos = self._calc_position(offset)
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
    ) -> 'Runner[T]':
        run = copy(self)
        vec = -1 if backward else 1
        if variable:
            while run.value(vec) in values:
                if not run.walk(vec):
                    break
        else:
            run._condition = run.value(vec) in values and run.walk(vec)
        return run

    def is_following(
        self, values: Sequence[T], /, variable: bool = False
    ) -> 'Runner[T]':
        return self.is_continuing(values, variable=variable, backward=True)

    def is_leading(
        self, values: Sequence[T], /, variable: bool = False
    ) -> 'Runner[T]':
        return self.is_continuing(values, variable=variable)

    def break_here(self) -> None:
        if self._text and self._breakables[self._position] == Breakable.Unknown:
            self._breakables[self._position] = Breakable.Break

    def do_not_break_here(self) -> None:
        if self._text and self._breakables[self._position] == Breakable.Unknown:
            self._breakables[self._position] = Breakable.DoNotBreak

    def does_break_here(self) -> bool:
        return bool(self._breakables[self._position])


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
