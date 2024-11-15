"""uniseg database lookup interface. """

from uniseg.db_lookups import columns, index1, index2, shift, values


def get_column_index(column_name: str) -> int:
    return columns.index(column_name)


def get_value(key: int, icolumn: int, /) -> str:
    index = index1[key >> shift]
    ivalue = index2[(index << shift) + (key & ((1 << shift) - 1))]
    return values[ivalue][icolumn]
