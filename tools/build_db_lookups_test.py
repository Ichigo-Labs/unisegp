import csv

base_dir = 'data/16.0.0/csv'


def get_break_tests(path):
    seq = list(csv.reader(open(path, 'r', encoding='utf-8')))
    s = "[\n"
    for elem in seq:
        s += "    " + repr(elem) + ',\n'
    s += "]\n"
    return s


form = f"""
word_break_test={get_break_tests(f'{base_dir}/auxiliary/WordBreakTest.csv')}
line_break_test={get_break_tests(f'{base_dir}/auxiliary/LineBreakTest.csv')}
sentence_break_test={get_break_tests(f'{base_dir}/auxiliary/SentenceBreakTest.csv')}
grapheme_cluster_break_test={get_break_tests(f'{base_dir}/auxiliary/GraphemeBreakTest.csv')}
"""


def main() -> None:
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument('infile', type=FileType('w', encoding='utf-8'))

    args = parser.parse_args()
    args.infile.write(form)


if __name__ == '__main__':
    main()
