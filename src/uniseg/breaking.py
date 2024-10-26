"""Breakable table and string tokenization."""

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Generic, Literal, Optional, TypeVar

__all__ = [
    'Breakable',
    'Breakables',
    'TailorFunc',
    'Runner',
    'boundaries',
    'break_units',
]


# type aliases for annotation
Breakable = Literal[0, 1]
Breakables = Iterable[Breakable]
TailorFunc = Callable[[str, Breakables], Breakables]


T = TypeVar('T')


class Runner(Generic[T]):

    def __init__(self, text: str, func: Callable[[str], T]):
        self._text = text
        self._values = [func(c) for c in text]
        self._skip = tuple[str, ...]()
        self._breakables: list[Literal[0, 1]] = [1 for __ in text]
        self._i = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def values(self) -> list[T]:
        return self._values

    @property
    def breakables(self) -> list[Literal[0, 1]]:
        return self._breakables

    @property
    def position(self) -> int:
        return self._i

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
        return self._text[self._i]

    def value(self, offset: int = 0) -> Optional[T]:
        i = self._i
        if offset == 0:
            return self._values[i] if 0 <= i < len(self._text) else None
        vec = offset // abs(offset)
        for __ in range(abs(offset)):
            i += vec
            while 0 <= i < len(self._text) and self._values[i] in self._skip:
                i += vec
        if 0 <= i < len(self._text):
            return self._values[i]
        return None

    def walk(self) -> bool:
        self._i += 1
        while self._i < len(self._text) and self._values[self._i] in self._skip:
            self._i += 1
        return self._i < len(self._text)

    def head(self) -> None:
        self._i = 0

    def skip(self, values: Sequence[T]) -> None:
        self._skip = tuple(values)

    def break_here(self) -> None:
        self._breakables[self._i] = 1

    def do_not_break_here(self) -> None:
        self._breakables[self._i] = 0

    def does_break_here(self) -> bool:
        return bool(self._breakables[self._i])


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
