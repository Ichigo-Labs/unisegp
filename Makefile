.PHONY: all \
        data ucd csv \
		code \
		docs \
		build test \
		pypi testpypi \
		install check_git_status \
        cleanall clean cleandata cleancsv cleanucd cleancode cleandocs

# project metadata
NAME = uniseg
UNICODE_VERSION = 15.0.0
UCD_BASE_URL = https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd


# directories
DIR_SRC = src
DIR_TESTS = tests
DIR_TOOLS = tools
DIR_DOCS = docs


# directories automatically created
SUBDIR_CSV = $(UNICODE_VERSION)/csv
SUBDIR_UCD = $(UNICODE_VERSION)/ucd

DIR_DATA = data
DIR_DATA_CSV = $(DIR_DATA)/$(SUBDIR_CSV)
DIR_DATA_UCD = $(DIR_DATA)/$(SUBDIR_UCD)
DIR_DIST = dist
DIR_DOCS_OUT = $(DIR_SRC)/$(NAME)/docs
DIR_DOCS_BUILD = $(DIR_DOCS)/_build
DIR_DOCS_BUILD_DOCTREE = $(DIR_DOCS)/_build/doctree

GENERATED_DIRS = $(DIR_DATA) $(DIR_DIST) $(DIR_DOCS_OUT)


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


# generated data files
UCD_PROP_FILES = \
    $(DIR_DATA_UCD)/auxiliary/GraphemeBreakProperty.txt \
	$(DIR_DATA_UCD)/auxiliary/SentenceBreakProperty.txt \
	$(DIR_DATA_UCD)/auxiliary/WordBreakProperty.txt \
	$(DIR_DATA_UCD)/emoji/emoji-data.txt \
	$(DIR_DATA_UCD)/LineBreak.txt
UCD_TEST_FILES = \
	$(DIR_DATA_UCD)/auxiliary/GraphemeBreakTest.txt \
	$(DIR_DATA_UCD)/auxiliary/SentenceBreakTest.txt \
	$(DIR_DATA_UCD)/auxiliary/WordBreakTest.txt \
	$(DIR_DATA_UCD)/auxiliary/LineBreakTest.txt
UCD_FILES = $(UCD_PROP_FILES) $(UCD_TEST_FILES)

CSV_PROP_FILES = $(patsubst $(DIR_DATA_UCD)/%.txt, $(DIR_DATA_CSV)/%.csv, $(UCD_PROP_FILES))
CSV_TEST_FILES = $(patsubst $(DIR_DATA_UCD)/%.txt, $(DIR_DATA_CSV)/%.csv, $(UCD_TEST_FILES))
CSV_FILES = $(CSV_PROP_FILES) $(CSV_TEST_FILES)


# generated code files
GREPHEME_RE_PY = $(DIR_SRC)/uniseg/grapheme_re.py
DB_LOOKUPS_PY = $(DIR_SRC)/uniseg/db_lookups.py
DB_LOOKUPS_TEST_PY = $(DIR_TESTS)/uniseg_db_lookups_test.py
GENERATED_CODE_FILES = $(GREPHEME_RE_PY) $(DB_LOOKUPS_PY) $(DB_LOOKUPS_TEST_PY)


# targets
all: data code docs $(GENERATED_CONTENTS)

data: ucd csv

ucd: $(UCD_FILES)

csv: $(CSV_FILES)

code: $(GENERATED_CODE_FILES)

$(GREPHEME_RE_PY): $(DIR_DATA_UCD)/auxiliary/GraphemeBreakProperty.txt \
                   $(DIR_DATA_UCD)/emoji/emoji-data.txt
	$(PYTHON) $(DIR_TOOLS)/build_grapheme_re.py -o $@ $^

$(DB_LOOKUPS_PY): $(CSV_PROP_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups.py $@

$(DB_LOOKUPS_TEST_PY): $(CSV_TEST_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups_test.py $@

docs:
	$(SPHINX_BUILD) -b html $(DIR_DOCS) $(DIR_DOCS_OUT)/html

build: all
	$(PYTHON) -m build -o $(DIR_DIST) .

test: code
	$(PYTEST)

pypi: check_git_status build
	$(TWINE) upload $(DIR_DIST)/*

testpypi: check_git_status build
	$(TWINE) upload -r testpypi --skip-existing $(DIR_DIST)/*

install:
	$(PIP) install -e '.[dev]'

check_git_status:
	@test -z "`git status -s`" || (echo "Repository is not clean" && exit 1)

cleanall: clean cleandata cleancode cleandocs
	-$(RM) -r $(DIR_SRC)/$(NAME).egg-info
	-$(RM) -r $(DIR_DIST)

clean:
	-$(RM) -r $(DIR_SRC)/**/__pycache__
	-$(RM) $(DIR_DIST)/*

cleandata: cleancsv cleanucd
	-$(RM) -r $(DIR_DATA)

cleancsv:
	-$(RM) -r $(DIR_DATA_CSV)

cleanucd:
	-$(RM) -r $(DIR_DATA_UCD)

cleancode:
	-$(RM) $(GENERATED_CODE_FILES)

cleandocs:
	-$(RM) -r $(DIR_DOCS_OUT) $(DIR_DOCS_BUILD)


# pattern rules

# csv files from ucd txt
$(DIR_DATA_CSV)/%Test.csv: $(DIR_DATA_UCD)/%Test.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/test2csv.py -p $(basename $(notdir $@)) -o $@ $<

$(DIR_DATA_CSV)/%.csv: $(DIR_DATA_UCD)/%.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/prop2csv.py -o $@ $<

# download ucd files
$(DIR_DATA_UCD)/%:
	$(CURL) --create-dirs -o $@ $(subst $(DIR_DATA_UCD),$(UCD_BASE_URL),$@)
