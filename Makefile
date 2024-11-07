.PHONY: all ucd gen docs build test \
		pypi testpypi \
		install check_git_status \
		cleanall clean cleanucd cleangen cleandocs

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
	$(DIR_UCD)/emoji/emoji-data.txt \
	$(DIR_UCD)/DerivedCoreProperties.txt

UCD_TEST_FILES = \
	$(DIR_UCD)/auxiliary/GraphemeBreakTest.txt \
	$(DIR_UCD)/auxiliary/WordBreakTest.txt \
	$(DIR_UCD)/auxiliary/SentenceBreakTest.txt \
	$(DIR_UCD)/auxiliary/LineBreakTest.txt

UCD_FILES = $(UCD_PROP_FILES) $(UCD_TEST_FILES)

# generated code

GEN_SRC_FILES = \
	 $(DIR_SRC)/uniseg/db_lookups.py

GEN_TEST_FILES = \
	$(DIR_TESTS)/test_graphemebreak.py \
	$(DIR_TESTS)/test_wordbreak.py \
	$(DIR_TESTS)/test_sentencebreak.py \
	$(DIR_TESTS)/test_linebreak.py

GEN_FILES = $(GEN_SRC_FILES) $(GEN_TEST_FILES)


# targets
all: ucd gen docs

ucd: $(UCD_FILES)

gen: $(GEN_FILES)

docs:
	$(SPHINX_BUILD) -b html $(DIR_DOCS) $(DIR_DOCS_OUT)/html

build: all
	$(PYTHON) -m build

test: gen
	$(PYTEST)

pypi: check_git_status build
	$(TWINE) upload $(DIR_DIST)/*

testpypi: check_git_status build
	$(TWINE) upload -r testpypi --skip-existing $(DIR_DIST)/*

install:
	$(PIP) install -e .

check_git_status:
	@test -z "`git status -s`" || (echo "Repository is not clean" && exit 1)

cleanall: clean cleanucd cleangen cleandocs
	-$(RM) -r $(DIR_SRC)/$(NAME).egg-info
	-$(RM) -r $(DIR_DIST)

clean:
	-$(RM) -r $(DIR_SRC)/**/__pycache__
	-$(RM) $(DIR_DIST)/*

cleanucd:
	-$(RM) -r $(DIR_UCD)

cleangen:
	-$(RM) $(GEN_FILES)

cleandocs:
	-$(RM) -r $(DIR_DOCS_OUT) $(DIR_DOCS_BUILD)


# generate source files

$(DIR_SRC)/uniseg/db_lookups.py: $(UCD_PROP_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups.py -o $@ \
		GraphemeClusterBreak=$(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
		WordBreak=$(DIR_UCD)/auxiliary/WordBreakProperty.txt \
		SentenceBreak=$(DIR_UCD)/auxiliary/SentenceBreakProperty.txt \
		LineBreak=$(DIR_UCD)/LineBreak.txt \
		$(DIR_UCD)/DerivedCoreProperties.txt \
		$(DIR_UCD)/emoji/emoji-data.txt


# generate test files

$(DIR_TESTS)/test_graphemebreak.py: $(DIR_UCD)/auxiliary/GraphemeBreakTest.txt
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py \
		-m uniseg.graphemecluster \
		-o $@ \
		grapheme_cluster_boundaries $^

$(DIR_TESTS)/test_wordbreak.py: $(DIR_UCD)/auxiliary/WordBreakTest.txt
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py \
		-m uniseg.wordbreak \
		-o $@ \
		word_boundaries $^

$(DIR_TESTS)/test_sentencebreak.py: $(DIR_UCD)/auxiliary/SentenceBreakTest.txt
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py \
		-m uniseg.sentencebreak \
		-o $@ \
		sentence_boundaries $^

$(DIR_TESTS)/test_linebreak.py: $(DIR_UCD)/auxiliary/LineBreakTest.txt
	$(PYTHON) $(DIR_TOOLS)/build_break_test.py \
		-m uniseg.linebreak \
		-o $@ \
		line_break_boundaries $^


# pattern rules

$(DIR_UCD)/%:
	$(CURL) --create-dirs -o $@ $(subst $(DIR_UCD),$(UCD_BASE_URL),$@)
