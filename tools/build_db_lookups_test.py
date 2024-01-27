import csv
import os

path = os.path.dirname(os.path.abspath(__file__))

def get_break_tests(path):
    seq = list(csv.reader(open(path, 'r')))
    s = "[\n"
    for elem in seq:
        s += "    " + repr(elem) + ',\n'
    s += "]\n"
    return s

form = f"""
word_break_test={get_break_tests(path + '/../csv/WordBreakTest.csv')}
line_break_test={get_break_tests(path + '/../csv/LineBreakTest.csv')}
sentence_break_test={get_break_tests(path + '/../csv/SentenceBreakTest.csv')}
grapheme_cluster_break_test={get_break_tests(path + '/../csv/GraphemeClusterBreakTest.csv')}
"""

def main() -> None:
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument('infile', type=FileType('w', encoding='utf-8'))

    args = parser.parse_args()
    args.infile.write(form)


if __name__ == '__main__':
    main()
