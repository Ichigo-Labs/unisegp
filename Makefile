.PHONY: all ucd csv clean build test upload docs testpypi pypi

# project metadata
NAME = uniseg
UNICODE_VERSION = 15.0.0
UCD_BASE_URL = http://www.unicode.org/Public/$(UNICODE_VERSION)/ucd


# directories
DIR_SRC = src
DIR_TESTS = tests
DIR_TOOLS = tools


# directories automatically created
DIR_CSV = data/$(UNICODE_VERSION)/csv
DIR_DIST = dist
DIR_DOCS = docs
DIR_UCD = data/$(UNICODE_VERSION)/ucd

GENERATED_DIRS = $(DIR_CSV) $(DIR_DIST)
ALL_GENERATED_DIRS = $(GENERATED_DIRS) $(DIR_DOCS) $(DIR_UCD)

DIR_DOCS_BUILD = docs/_build


# commands
CURL = curl --compressed
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
    $(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
	$(DIR_UCD)/auxiliary/SentenceBreakProperty.txt \
	$(DIR_UCD)/auxiliary/WordBreakProperty.txt \
	$(DIR_UCD)/emoji/emoji-data.txt \
	$(DIR_UCD)/LineBreak.txt
UCD_TEST_FILES = \
	$(DIR_UCD)/auxiliary/GraphemeBreakTest.txt \
	$(DIR_UCD)/auxiliary/SentenceBreakTest.txt \
	$(DIR_UCD)/auxiliary/WordBreakTest.txt \
	$(DIR_UCD)/auxiliary/LineBreakTest.txt
UCD_FILES = $(UCD_PROP_FILES) $(UCD_TEST_FILES)

CSV_PROP_FILES = $(patsubst $(DIR_UCD)/%.txt, $(DIR_CSV)/%.csv, $(UCD_PROP_FILES))
CSV_TEST_FILES = $(patsubst $(DIR_UCD)/%.txt, $(DIR_CSV)/%.csv, $(UCD_TEST_FILES))
CSV_FILES = $(CSV_PROP_FILES) $(CSV_TEST_FILES)


# generated code files
GREPHEME_RE_PY = $(DIR_SRC)/uniseg/grapheme_re.py
DB_LOOKUPS_PY = $(DIR_SRC)/uniseg/db_lookups.py
DB_LOOKUPS_TEST_PY = $(DIR_TESTS)/uniseg_db_lookups_test.py
GENERATED_CODE_FILES = $(GREPHEME_RE_PY) $(DB_LOOKUPS_PY) $(DB_LOOKUPS_TEST_PY)


# targets
all: $(GENERATED_CODE_FILES)

$(GREPHEME_RE_PY): $(DIR_UCD)/auxiliary/GraphemeBreakProperty.txt \
                   $(DIR_UCD)/emoji/emoji-data.txt
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
# Use 'mkdir -p' instead of --create-dirs option of curl because it
# doesn't work well with path names with '/' on Windows.
$(DIR_UCD)/%:
	-$(MKDIR) -p $(dir $@)
	$(CURL) -o $@ $(subst $(DIR_UCD),$(UCD_BASE_URL),$@)
