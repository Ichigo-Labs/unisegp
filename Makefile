.PHONY: all ucd csv clean build test upload docs testpypi pypi

# project metadata
NAME = uniseg
UNICODE_VERSION = 15.0.0
UCD_BASE_URL = http://www.unicode.org/Public


# directories
DIR_SRC = src
DIR_TESTS = tests
DIR_TOOLS = tools


# directories automatically created
PATH_CSV = $(UNICODE_VERSION)/csv
PATH_UCD = $(UNICODE_VERSION)/ucd

DIR_DATA = data
DIR_DATA_CSV = $(DIR_DATA)/$(PATH_CSV)
DIR_DATA_UCD = $(DIR_DATA)/$(PATH_UCD)
DIR_DIST = dist
DIR_DOCS = docs
DIR_DOCS_BUILD = $(DIR_DOCS)/_build

GENERATED_DIRS = $(DIR_DATA) $(DIR_DIST)


# commands
CURL = curl --compressed --create-dirs
MKDIR = "mkdir"
MV = mv
PIP = python -m pip
PYTEST = pytest
PYTHON = python
RM = rm -v
SPHINX_BUILD = sphinx-build
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

CSV_PROP_FILES = $(patsubst $(PATH_UCD)/%.txt, $(PATH_CSV)/%.csv, $(UCD_PROP_FILES))
CSV_TEST_FILES = $(patsubst $(PATH_UCD)/%.txt, $(PATH_CSV)/%.csv, $(UCD_TEST_FILES))
CSV_FILES = $(CSV_PROP_FILES) $(CSV_TEST_FILES)


# generated code files
GREPHEME_RE_PY = $(DIR_SRC)/uniseg/grapheme_re.py
DB_LOOKUPS_PY = $(DIR_SRC)/uniseg/db_lookups.py
DB_LOOKUPS_TEST_PY = $(DIR_TESTS)/uniseg_db_lookups_test.py
GENERATED_CODE_FILES = $(GREPHEME_RE_PY) $(DB_LOOKUPS_PY) $(DB_LOOKUPS_TEST_PY)


# targets
all: $(GENERATED_CODE_FILES)

$(GREPHEME_RE_PY): $(DIR_DATA_UCD)/auxiliary/GraphemeBreakProperty.txt \
                   $(DIR_DATA_UCD)/emoji/emoji-data.txt
	$(PYTHON) $(DIR_TOOLS)/build_grapheme_re.py -o $@ $^

$(DB_LOOKUPS_PY): $(CSV_PROP_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups.py $@

$(DB_LOOKUPS_TEST_PY): $(CSV_TEST_FILES)
	$(PYTHON) $(DIR_TOOLS)/build_db_lookups_test.py $@

csv: $(CSV_FILES)

ucd: $(UCD_FILES)

build: all
	$(PYTHON) -m build .

test: all
	$(PYTEST)

clean:
	-$(RM) $(GENERATED_CODE_FILES)
	-$(RM) -r $(DIR_SRC)/$(NAME)/__pycache__
	-$(RM) -r csv

cleanall: clean cleandocs
	-$(RM) -r $(DIR_UCD)
	-$(RM) -r $(DIR_SRC)/$(NAME).egg-info
	-$(RM) -r dist
	-$(RM) -r build

testpypi: sdist wheel
	$(TWINE) upload -r testpypi --skip-existing dist/*

pypi: sdist wheel
	$(TWINE) upload dist/*

install:
	$(PIP) install -e '.[dev]'

docs:
	$(SPHINX_BUILD) -b html $(DIR_DOCS) $(DIR_DOCS_BUILD)/html

cleandocs:
	-$(RM) -r $(DIR_DOCS_BUILD)


# pattern rules

# csv files from ucd txt
$(DIR_CSV)/%Test.csv: $(DIR_UCD)/%Test.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/test2csv.py -p $(basename $(notdir $@)) -o $@ $<

$(DIR_CSV)/%.csv: $(DIR_UCD)/%.txt
	-$(MKDIR) -p $(dir $@)
	$(PYTHON) $(DIR_TOOLS)/prop2csv.py -o $@ $<

# download ucd files
$(DIR_DATA_UCD)/%:
	$(CURL) -o $@ $(subst $(DIR_DATA),$(UCD_BASE_URL),$@)
