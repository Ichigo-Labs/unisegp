"""uniseg database lookup interface. """

from uniseg.db_lookups import columns, index1, index2, shift, values

INDEX_LINE_BREAK = columns.index('LineBreak')


def get_column_index(column_name: str) -> int:
    return columns.index(column_name)


def get_value(key: int, icolumn: int, /) -> str:
    index = index1[key >> shift]
    ivalue = index2[(index << shift) + (key & ((1 << shift) - 1))]
    return values[ivalue][icolumn]


def line_break(ch: str, /) -> str:
    return get_value(ord(ch), INDEX_LINE_BREAK) or 'XX'
