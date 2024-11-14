"""Emoji Data for UTS #51.

`UTS #51: Unicode Emoji (16.0)
<https://www.unicode.org/reports/tr51/tr51-27.html>`_
"""

from uniseg.db import get_column_index, get_value

INDEX_EXTENDED_PICTOGRAPHIC = get_column_index('Extended_Pictographic')


def extended_pictographic(ch: str, /) -> bool:
    return bool(get_value(ord(ch), INDEX_EXTENDED_PICTOGRAPHIC))
