"""Emoji Data for UTS #51.

`UTS #51: Unicode Emoji (16.0)
<https://www.unicode.org/reports/tr51/tr51-27.html>`_
"""

from uniseg.db import get_column_index, get_value

__all__ = [
    'emoji',
    'emoji_presentation',
    'emoji_modifier_base',
    'emoji_component',
    'extended_pictographic',
]

INDEX_EMOJI = get_column_index('Emoji')
INDEX_EMOJI_PRESENTATION = get_column_index('Emoji_Presentation')
INDEX_EMOJI_MODIFIER_BASE = get_column_index('Emoji_Modifier_Base')
INDEX_EMOJI_COMPONENT = get_column_index('Emoji_Component')
INDEX_EXTENDED_PICTOGRAPHIC = get_column_index('Extended_Pictographic')


def emoji(ch: str, /) -> bool:
    """Return Emoji boolean Unicode property value for `ch`.

    >>> emoji('A')
    False
    >>> emoji('🐸')
    True
    """
    return bool(get_value(ord(ch), INDEX_EMOJI))


def emoji_presentation(ch: str, /) -> bool:
    """Return Emoji_Presentation boolean Unicode property value for `ch`.

    >>> emoji_presentation('A')
    False
    >>> emoji_presentation('🌞')
    True
    """
    return bool(get_value(ord(ch), INDEX_EMOJI_PRESENTATION))


def emoji_modifier_base(ch: str, /) -> bool:
    """Return Emoji_Modifier_Base boolean Unicode property value for `ch`.

    >>> emoji_modifier_base('A')
    False
    >>> emoji_modifier_base('👼')
    True
    """
    return bool(get_value(ord(ch), INDEX_EMOJI_MODIFIER_BASE))


def emoji_component(ch: str, /) -> bool:
    """Return Emoji_Component boolean Unicode property value for `ch`.

    >>> emoji_component('A')
    False
    >>> emoji_component('#')
    True
    """
    return bool(get_value(ord(ch), INDEX_EMOJI_COMPONENT))


def extended_pictographic(ch: str, /) -> bool:
    """Return Extended_Pictographic boolean Unicode property value for `ch`.

    >>> extended_pictographic('A')
    False
    >>> extended_pictographic('🐤')
    True
    """
    return bool(get_value(ord(ch), INDEX_EXTENDED_PICTOGRAPHIC))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
