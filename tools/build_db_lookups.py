import array
import csv
import sys
from collections.abc import Sequence

base_dir = 'data/15.0.0/csv'

reader = csv.reader(open(f'{base_dir}/auxiliary/WordBreakProperty.csv', 'r'))
WordBreak = {int(k): v for k, v in reader}
reader = csv.reader(open(f'{base_dir}/LineBreak.csv', 'r'))
LineBreak = {int(k): v for k, v in reader}
reader = csv.reader(
    open(f'{base_dir}/auxiliary/SentenceBreakProperty.csv', 'r'))
SentenceBreak = {int(k): v for k, v in reader}
reader = csv.reader(
    open(f'{base_dir}/auxiliary/GraphemeBreakProperty.csv', 'r'))
GraphemeClusterBreak = {int(k): v for k, v in reader}

mapping = [
    (
        WordBreak.get(x, 'Other'),
        LineBreak.get(x, 'Other'),
        SentenceBreak.get(x, 'Other'),
        GraphemeClusterBreak.get(x, 'Other'),
    )
    for x in range(sys.maxunicode + 1)
]


def getsize(data: Sequence) -> int:
    """return smallest possible integer size for the given array. """

    maxdata = max(data)
    if maxdata < 0x100:
        return 1
    if maxdata < 0x10000:
        return 2
    return 4


def splitbins(t: Sequence[int]) -> tuple[list[int], list[int], int]:
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
    t = tuple(t)        # so slices can be dict keys
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


unique = [x for x in sorted(set(mapping))]

index = [unique.index(x) for x in mapping]
index1, index2, shift = splitbins(index)


index1_arr = array.array('B')
index1_arr.extend(index1)
index1_bytes = index1_arr.tobytes()

index2_arr = array.array('B')
index2_arr.extend(index2)
index2_bytes = index2_arr.tobytes()

form = f"""
shift={shift}
word_break_list={repr([x[0] for x in unique])}
line_break_list={repr([x[1] for x in unique])}
sentence_break_list={repr([x[2] for x in unique])}
grapheme_cluster_break_list={repr([x[3] for x in unique])}
index1={repr(index1_bytes)}
index2={repr(index2_bytes)}
"""


def main() -> None:
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument('infile', type=FileType('w', encoding='utf-8'))

    args = parser.parse_args()
    args.infile.write(form)


if __name__ == '__main__':
    main()
