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

with open(path + '/../uniseg/db_lookups_test.py', 'w') as f:
    f.write(form)
