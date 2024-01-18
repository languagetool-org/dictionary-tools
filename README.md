[![Flake8](https://github.com/languagetool-org/dictionary-tools/actions/workflows/flake8.yml/badge.svg)](https://github.com/languagetool-org/dictionary-tools/actions/workflows/flake8.yml)
[![Pytest](https://github.com/languagetool-org/dictionary-tools/actions/workflows/pytest.yml/badge.svg)](https://github.com/languagetool-org/dictionary-tools/actions/workflows/pytest.yml)

# Dictionary Tools
This repository contains tools for compiling and deploying dictionaries for [LanguageTool](https://languagetool.org/).

## Maintainer

The owner, maintainer, and main dev for this repository is @p-goulart. Any potential shell and perl components may be
better explained by @jaumeortola, though.

## Setup

### Python dependencies

This is set up as a Poetry project, so you must have [Poetry](https://python-poetry.org/docs/) installed and ready to go.

Make sure you are using a [virtual environment](https://python-poetry.org/docs/managing-environments/) and then:

```bash
poetry install --with test,dev
```

### System dependencies

In addition to the Python dependencies, you will also need to have [Hunspell](https://github.com/hunspell/hunspell)
binaries installed on your system.

The most important one is `unmunch`. Check if it's installed:

```bash
which unmunch
# should return a path to a bin directory, like
# /opt/homebrew/bin/unmunch
```

If it's not installed, you may need to compile Hunspell from source. Clone the [Hunspell repo](https://github.com/hunspell/hunspell)
and then, from inside it, these steps should work on Ubuntu:
```bash
# install a bunch of dependencies needed for compilation
sudo apt-get install autoconf automake autopoint libtool
autoreconf -vfi
./configure
make
sudo make install
sudo ldconfig
```

### LT dependencies

The scripts here also depend on the `languagetool` Java codebase (for word tokenisation).

Make sure you have LT cloned locally, and export the following environment variable in your shell configuration:

```bash
export LT_HOME=/path/to/languagetool
```

If this is not done, the code in this project will set that variable as a default to `../languagetool` (meaning one
directory up from wherever this repo is cloned).

## Usage

This repository should be a submodule of language-specific repositories. For example, the [Portuguese repository](https://github.com/languagetool-org/portuguese-pos-dict).

⚠️ Note that the name of this repository is in **kebab-case**, but Python modules should be imported in **snake_case**.
Therefore, when importing this as a submodule, make sure to set the path to `dict_tools`, which uses the underscore.
If you don't do this, you may fail to import it as a module.

### `build_tagger_dicts.py`

This is the script that takes compiles source files into a binary dictionary to be used by the LT POS tagger, Word
Tokeniser, and Synthesiser.

You can check the usage parameters by invoking it with `--help`:

```bash
poetry run python scripts/build_tagger_dicts.py --help
```

### `build_spelling_dicts.py`

This is the script that takes all the Hunspell and helper files as input and yields as output binary files to be used
by the Morfologik speller.

You can check the usage parameters by invoking it with `--help`:

```bash
poetry run python scripts/build_spelling_dicts.py --help
```
