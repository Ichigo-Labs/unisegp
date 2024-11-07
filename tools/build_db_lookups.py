import array
import sys
from argparse import ArgumentParser, FileType
from dataclasses import dataclass
from itertools import groupby
from pprint import pformat
from typing import Optional, TextIO

from ucdtools import iter_code_point_properties


def getsize(data: list) -> int:
    """return smallest possible integer size for the given array. """
    maxdata = max(data)
    if maxdata < 0x100:
        return 1
    if maxdata < 0x10000:
        return 2
    return 4


def splitbins(t: tuple[int, ...]) -> tuple[list[int], list[int], int]:
    """t, trace=0 -> (t1, t2, shift).  Split a table to save space.
    t is a sequence of ints.  This function can be useful to save space if
    many of the ints are the same.  t1 and t2 are lists of ints, and shift
    is an int, chosen to minimize the combined size of t1 and t2 (in C
    code), and where for each i in range(len(t)),
        t[i] == t2[(t1[i >> shift] << shift) + (i & mask)]
    where mask is a bitmask isolating the last "shift" bits.
    """
    n = len(t) - 1  # last valid index
    maxshift = 0    # the most we can shift n and still have something left
    if n > 0:
        while n >> 1:
            n >>= 1
            maxshift += 1
    del n

    bytes = sys.maxsize  # smallest total size so far
    for shift in range(maxshift + 1):
        t1 = []
        t2 = []
        size = 2 ** shift
        bincache = {}
        for i in range(0, len(t), size):
            bin = t[i:i+size]
            index = bincache.get(bin)
            if index is None:
                index = len(t2)
                bincache[bin] = index
                t2.extend(bin)
            t1.append(index >> shift)
        # determine memory size
        b = len(t1) * getsize(t1) + len(t2) * getsize(t2)
        if b < bytes:
            best = t1, t2, shift
            bytes = b
    t1, t2, shift = best
    return best


@dataclass(init=False)
class PropArg:
    """A data class which represents a property argument."""
    name: str
    stream: TextIO

    def __init__(self, arg: str):
        if '=' in arg:
            name_part, path_part = arg.split('=', 1)
            name_part = name_part.strip()
            path_part = path_part.strip()
        else:
            name_part = ''
            path_part = arg.strip()
        self.name = name_part.strip()
        if path_part == '-':
            self.stream = sys.stdin
        else:
            self.stream = open(path_part, 'r', encoding='utf-8')


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument('-o', '--output', default='-',
                        type=FileType('w', encoding='utf-8'))
    parser.add_argument('files', nargs='+',
                        type=PropArg,
                        help='UCD property files')
    args = parser.parse_args()
    output: TextIO = args.output
    prop_args: list[PropArg] = args.files

    names = list[str]()
    db = [list[Optional[str]]() for cp in range(sys.maxunicode + 1)]
    for prop_arg in prop_args:
        name = prop_arg.name
        stream = prop_arg.stream
        items = iter_code_point_properties(stream)
        if name:
            # named property
            print(name, file=sys.stderr)
            names.append(name)
            item_dict = dict(items)
            for cp in range(sys.maxunicode + 1):
                record = item_dict.get(cp)
                value = record.fields[0] if record else ''
                db[cp].append(value)
        else:
            # unnamed property
            for name, grouped_items in groupby(items, lambda x: x[1].fields[0]):
                print(name, file=sys.stderr)
                names.append(name)
                item_dict = dict(grouped_items)
                for cp in range(sys.maxunicode + 1):
                    record = item_dict.get(cp)
                    if record:
                        if len(record.fields) == 1:
                            value = 'Y'
                        elif len(record.fields) == 2:
                            value = record.fields[1]
                        else:
                            raise ValueError(f'{len(record.fields)}=')
                    else:
                        value = ''
                    db[cp].append(value)

    sparse_records = tuple(tuple(items) for items in db)
    unique_records = tuple(sorted(set(sparse_records)))
    indices = tuple(unique_records.index(x) for x in sparse_records)
    index1, index2, shift = splitbins(indices)
    bytes1 = array.array('B', index1).tobytes()
    bytes2 = array.array('B', index2).tobytes()

    code = (
        f'# DO NOT EDIT.  This file is generated automatically.\n'
        f'columns = \\\n{pformat(tuple(names), compact=True)}\n'
        f'values = \\\n{pformat(unique_records, compact=True)}\n'
        f'shift = {shift}\n'
        f'index1 = \\\n{pformat(bytes1, compact=True)}\n'
        f'index2 = \\\n{pformat(bytes2, compact=True)}\n'
    )
    output.write(code)


if __name__ == '__main__':
    main()
