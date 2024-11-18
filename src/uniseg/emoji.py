"""Emoji Data for UTS #51.

`UTS #51: Unicode Emoji (16.0)
<https://www.unicode.org/reports/tr51/tr51-27.html>`_
"""

from uniseg.db import get_handle, get_value

__all__ = [
    'emoji',
    'emoji_presentation',
    'emoji_modifier_base',
    'emoji_component',
    'extended_pictographic',
]


H_EMOJI = get_handle('Emoji')
H_EMOJI_PRESENTATION = get_handle('Emoji_Presentation')
H_EMOJI_MODIFIER_BASE = get_handle('Emoji_Modifier_Base')
H_EMOJI_COMPONENT = get_handle('Emoji_Component')
H_EXTENDED_PICTOGRAPHIC = get_handle('Extended_Pictographic')


def emoji(c: str, /) -> bool:
    """Return Emoji boolean Unicode property value for `c`.

    >>> emoji('A')
    False
    >>> emoji('🐸')
    True
    """
    return bool(get_value(H_EMOJI, ord(c)))


def emoji_presentation(c: str, /) -> bool:
    """Return Emoji_Presentation boolean Unicode property value for `c`.

    >>> emoji_presentation('A')
    False
    >>> emoji_presentation('🌞')
    True
    """
    return bool(get_value(H_EMOJI_PRESENTATION, ord(c)))


def emoji_modifier_base(c: str, /) -> bool:
    """Return Emoji_Modifier_Base boolean Unicode property value for `c`.

    >>> emoji_modifier_base('A')
    False
    >>> emoji_modifier_base('👼')
    True
    """
    return bool(get_value(H_EMOJI_MODIFIER_BASE, ord(c)))


def emoji_component(c: str, /) -> bool:
    """Return Emoji_Component boolean Unicode property value for `c`.

    >>> emoji_component('A')
    False
    >>> emoji_component('#')
    True
    """
    return bool(get_value(H_EMOJI_COMPONENT, ord(c)))


def extended_pictographic(c: str, /) -> bool:
    """Return Extended_Pictographic boolean Unicode property value for `c`.

    >>> extended_pictographic('A')
    False
    >>> extended_pictographic('🐤')
    True
    """
    return bool(get_value(H_EXTENDED_PICTOGRAPHIC, ord(c)))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
