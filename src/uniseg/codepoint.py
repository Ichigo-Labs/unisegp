"""Unicode code point. """

from builtins import ord as _ord, chr as _chr
from typing import Optional, Iterator


__all__ = [
    'ord',
    'chr',
    'code_points'
]


def ord(c: str, index: Optional[int] = None, /) -> int:

    """Return the integer value of the Unicode code point `c`

    >>> ord('a')
    97
    >>> ord('\\u3042')
    12354
    >>> ord('\\U00020b9f')
    134047
    >>> ord('abc')
    Traceback (most recent call last):
      ...
    TypeError: need a single Unicode code point as parameter

    It returns the result of built-in ord() when `c` is a single str
    object for compatibility:

    >>> ord('a')
    97

    When `index` argument is specified (to not ``None``), this function
    treats `c` as a Unicode string and returns integer value of code
    point at ``c[index]`` (or may be ``c[index:index+2]``):

    >>> ord('hello', 0)
    104
    >>> ord('hello', 1)
    101
    >>> ord('a\\U00020b9f', 1)
    134047
    """

    return _ord(c if index is None else c[index])


def chr(cp: int, /) -> str:

    """Return the unicode object represents the code point integer `cp`

    >>> chr(0x61) == 'a'
    True
    >>> chr(0x20b9f) == '\\U00020b9f'
    True
    """

    return _chr(cp)


def code_point(s: str, index: int = 0, /) -> str:

    """Return code point at s[index]

    >>> code_point('ABC') == 'A'
    True
    >>> code_point('ABC', 1) == 'B'
    True
    >>> code_point('\\U00020b9f\\u3042') == '\\U00020b9f'
    True
    >>> code_point('\\U00020b9f\\u3042', 1) == '\\u3042'
    True
    """

    return s[index]


def code_points(s: str, /) -> Iterator[str]:

    """Iterate every Unicode code points of the unicode string `s`

    >>> s = 'hello'
    >>> list(code_points(s)) == ['h', 'e', 'l', 'l', 'o']
    True
    >>> s = 'abc\\U00020b9f\\u3042'
    >>> list(code_points(s)) == ['a', 'b', 'c', '\\U00020b9f', '\\u3042']
    True
    """

    return iter(s)


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
