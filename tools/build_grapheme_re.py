from argparse import ArgumentParser, FileType
from itertools import chain
from typing import Dict, List, TextIO, cast

from ucdtools import CodePointRange, iter_records, group_continuous


OTHER = 'Other'
CR = 'CR'
LF = 'LF'
CONTROL = 'Control'
EXTEND = 'Extend'
ZWJ = 'ZWJ'
RI = REGIONAL_INDICATOR = 'Regional_Indicator'
PREPEND = 'Prepend'
SPACINGMARK = 'SpacingMark'
L = 'L'
V = 'V'
T = 'T'
LV = 'LV'
LVT = 'LVT'

EXTENDED_PICTOGRAPHIC = 'Extended_Pictographic'


def generate_pattern(cprange_dict: Dict[str, List[CodePointRange]]) -> str:

    # charset[prop_value] -> re_charset_pattern
    charset: Dict[str, str] = {}

    for prop_value, cpranges in cprange_dict.items():
        re_character_set = f'{"".join(cpr.re_chars() for cpr in cpranges)}'
        charset[prop_value] = re_character_set

    # build patterns.
    pat_crlf = f"{charset[CR]}{charset[LF]}"
    pat_control = f"[{charset[CONTROL]}]"
    pat_postcore = f"[{charset[EXTEND]}{charset[ZWJ]}{charset[SPACINGMARK]}]"
    pat_precore = f"[{charset[PREPEND]}]"
    pat_ri_sequence = f"{charset[RI]}{charset[RI]}"
    pat_hangul_syllable = (
        f"(?:"
        f"[{charset[L]}]*"
        f"(?:[{charset[V]}]+|[{charset[LV]}][{charset[V]}]*|[{charset[LVT]}])"
        f"[{charset[T]}]*"
        f"|"
        f"[{charset[L]}]+"
        f"|"
        f"[{charset[T]}]+"
        f")"
    )
    pat_xpicto_sequence = (
        f"[{charset[EXTENDED_PICTOGRAPHIC]}]"
        f"(?:"
        f"[{charset[EXTEND]}]*"
        f"[{charset[ZWJ]}]"
        f"[{charset[EXTENDED_PICTOGRAPHIC]}]"
        f")*"
    )
    pat_core = (
        f"(?:"
        f"{pat_hangul_syllable}"
        f"|"
        f"{pat_ri_sequence}"
        f"|"
        f"{pat_xpicto_sequence}"
        f"|"
        f"[^{charset[CONTROL]}{charset[ZWJ]}{charset[SPACINGMARK]}]"
        f")"
    )
    pat_extended_grapheme_cluster = (
        f"(?:"
        f"{pat_crlf}"
        f"|"
        f"{pat_control}"
        f"|"
        f"{pat_precore}*{pat_core}{pat_postcore}*"
        f")"
    )
    return pat_extended_grapheme_cluster


def optimize_code_point_ranges(
        cpranges: List[CodePointRange]) -> List[CodePointRange]:
    """Return re-ordered / optimized `CodePointRange` object list. """

    code_points = list(chain.from_iterable(cpranges))
    code_points.sort()

    new_cpranges: List[CodePointRange] = []
    for grouped_iter in group_continuous(code_points):
        grouped_cps = list(grouped_iter)
        cp1 = grouped_cps[0]
        cp2 = grouped_cps[-1] if len(grouped_cps) > 1 else None
        cprange = CodePointRange(cp1, cp2)
        new_cpranges.append(cprange)
    return new_cpranges


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument('-o', '--output', type=FileType('w'), default='-')
    parser.add_argument('path_grapheme_breake_property_txt')
    parser.add_argument('path_emoji_data_txt')
    args = parser.parse_args()

    gcb_file_name = str(args.path_grapheme_breake_property_txt)
    emoji_file_name = str(args.path_emoji_data_txt)
    fout = cast(TextIO, args.output)

    # prop_to_cpranges[prop_value] -> list_of_code_point_ranges
    prop_to_cpranges: Dict[str, List[CodePointRange]] = {}

    with open(gcb_file_name) as f:
        for fields in iter_records(f):
            if len(fields) != 2:
                continue
            f1, f2 = fields
            cprange = CodePointRange.from_literal(f1)
            prop_value = f2
            prop_to_cpranges.setdefault(prop_value, []).append(cprange)

    with open(emoji_file_name, encoding='utf-8') as f:
        for fields in iter_records(f):
            if not (len(fields) == 2 and fields[1] == EXTENDED_PICTOGRAPHIC):
                continue
            f1, f2 = fields
            cprange = CodePointRange.from_literal(f1)
            prop_value = f2
            prop_to_cpranges.setdefault(prop_value, []).append(cprange)

    # Optimize code points rangees
    for prop_value, cpranges in prop_to_cpranges.items():
        cpranges[:] = optimize_code_point_ranges(cpranges)

    PAT_EXTENDED_GRAPHEME_CLUSTER = generate_pattern(prop_to_cpranges)
    print('\n'.join([
        '# DO NOT EDIT. This file is generated automatically.',
        f'{PAT_EXTENDED_GRAPHEME_CLUSTER=}',
    ]), file=fout)


if __name__ == '__main__':
    main()
