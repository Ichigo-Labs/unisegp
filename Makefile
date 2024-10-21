.PHONY: all ucd csv code docs build test \
		pypi testpypi \
		install check_git_status \
		cleanall clean cleancsv cleanucd cleancode cleandocs

# project

NAME = uniseg
UNICODE_VERSION = 16.0.0
UCD_BASE_URL = https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd


# directories

DIR_SRC = src
DIR_TESTS = tests
DIR_TOOLS = tools
DIR_DOCS = docs
DIR_DATA = data
DIR_CSV = $(DIR_DATA)/$(UNICODE_VERSION)/csv
DIR_UCD = $(DIR_DATA)/$(UNICODE_VERSION)/ucd
DIR_DIST = dist
DIR_DOCS_OUT = $(DIR_SRC)/$(NAME)/docs
DIR_DOCS_BUILD = $(DIR_DOCS)/_build
DIR_DOCS_BUILD_DOCTREE = $(DIR_DOCS)/_build/doctree


# commands

MV = mv
RM = rm -v
MKDIR = mkdir
CURL = curl -s
PYTHON = python
PIP = python -m pip
PYTEST = pytest
SPHINX_BUILD = python -m sphinx.cmd.build -q -d $(DIR_DOCS_BUILD_DOCTREE)
TWINE = twine


# data files

UCD_PROP_FILES = \
    $(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
	$(DIR_UCD)/auxiliary/WordBreakProperty.txt \
	$(DIR_UCD)/auxiliary/SentenceBreakProperty.txt \
	$(DIR_UCD)/LineBreak.txt \
	$(DIR_UCD)/emoji/emoji-data.txt

UCD_TEST_FILES = \
	$(DIR_UCD)/auxiliary/GraphemeBreakTest.txt \
	$(DIR_UCD)/auxiliary/WordBreakTest.txt \
	$(DIR_UCD)/auxiliary/LineBreakTest.txt \
	$(DIR_UCD)/auxiliary/SentenceBreakTest.txt

UCD_FILES = $(UCD_PROP_FILES) $(UCD_TEST_FILES)

CSV_PROP_FILES = \
	$(patsubst $(DIR_UCD)/%.txt, $(DIR_CSV)/%.csv, $(UCD_PROP_FILES))

CSV_TEST_FILES = \
	$(patsubst $(DIR_UCD)/%.txt, $(DIR_CSV)/%.csv, $(UCD_TEST_FILES))

CSV_FILES = $(CSV_PROP_FILES) $(CSV_TEST_FILES)


# generated code

GEN_SRC_FILES = \
	 $(DIR_SRC)/uniseg/db_lookups.py \
	 $(DIR_SRC)/uniseg/grapheme_re.py

GEN_TEST_FILES = \
	$(DIR_TESTS)/test_graphemebreak.py \
	$(DIR_TESTS)/test_wordbreak.py \
	$(DIR_TESTS)/test_linebreak.py \
	$(DIR_TESTS)/test_sentencebreak.py

GEN_FILES = $(GEN_SRC_FILES) $(GEN_TEST_FILES)


# targets
all: ucd csv code docs

ucd: $(UCD_FILES)

csv: $(CSV_FILES)

code: $(GEN_FILES)

docs:
	$(SPHINX_BUILD) -b html $(DIR_DOCS) $(DIR_DOCS_OUT)/html

build: all
	$(PYTHON) -m build

test: code
	$(PYTEST)

pypi: check_git_status build
	$(TWINE) upload $(DIR_DIST)/*

testpypi: check_git_status build
	$(TWINE) upload -r testpypi --skip-existing $(DIR_DIST)/*

install:
	$(PIP) install -e .

check_git_status:
	@test -z "`git status -s`" || (echo "Repository is not clean" && exit 1)

cleanall: clean cleancsv cleanucd cleancode cleandocs
	-$(RM) -r $(DIR_SRC)/$(NAME).egg-info
	-$(RM) -r $(DIR_DIST)

clean:
	-$(RM) -r $(DIR_SRC)/**/__pycache__
	-$(RM) $(DIR_DIST)/*

cleancsv:
	-$(RM) -r $(DIR_CSV)

cleanucd:
	-$(RM) -r $(DIR_UCD)

cleancode:
	-$(RM) $(GEN_FILES)

cleandocs:
	-$(RM) -r $(DIR_DOCS_OUT) $(DIR_DOCS_BUILD)


# generate source files

$(DIR_SRC)/uniseg/db_lookups.py: $(DIR_TOOLS)/build_db_lookups.py \
		$(CSV_PROP_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups.py $@

$(DIR_SRC)/uniseg/grapheme_re.py: $(DIR_TOOLS)/build_grapheme_re.py \
		$(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
		$(DIR_UCD)/emoji/emoji-data.txt
	$(PYTHON) $(DIR_TOOLS)/build_grapheme_re.py -o $@ \
		$(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
		$(DIR_UCD)/emoji/emoji-data.txt


# generate test files

$(DIR_TESTS)/test_graphemebreak.py: $(DIR_TOOLS)/build_break_test.py \
		$(DIR_CSV)/auxiliary/GraphemeBreakTest.csv
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py -m uniseg.graphemecluster -o $@ \
		grapheme_cluster_boundaries $(DIR_CSV)/auxiliary/GraphemeBreakTest.csv

$(DIR_TESTS)/test_wordbreak.py: $(DIR_TOOLS)/build_break_test.py \
		$(DIR_CSV)/auxiliary/WordBreakTest.csv
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py -m uniseg.wordbreak -o $@ \
		word_boundaries $(DIR_CSV)/auxiliary/WordBreakTest.csv

$(DIR_TESTS)/test_linebreak.py: $(DIR_TOOLS)/build_break_test.py \
		$(DIR_CSV)/auxiliary/LineBreakTest.csv
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py -m uniseg.linebreak -o $@ \
		line_break_boundaries $(DIR_CSV)/auxiliary/LineBreakTest.csv

$(DIR_TESTS)/test_sentencebreak.py: $(DIR_TOOLS)/build_break_test.py \
		$(DIR_CSV)/auxiliary/SentenceBreakTest.csv
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py -m uniseg.sentencebreak -o $@ \
		sentence_boundaries $(DIR_CSV)/auxiliary/SentenceBreakTest.csv


# pattern rules

$(DIR_UCD)/%:
	$(CURL) --create-dirs -o $@ $(subst $(DIR_UCD),$(UCD_BASE_URL),$@)

$(DIR_CSV)/%Test.csv: $(DIR_UCD)/%Test.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/test2csv.py -p $(basename $(notdir $@)) -o $@ $<

$(DIR_CSV)/%.csv: $(DIR_UCD)/%.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/prop2csv.py -o $@ $<
