[![Flake8](https://github.com/languagetool-org/dictionary-tools/actions/workflows/flake8.yml/badge.svg)](https://github.com/languagetool-org/dictionary-tools/actions/workflows/flake8.yml)
[![Pytest](https://github.com/languagetool-org/dictionary-tools/actions/workflows/pytest.yml/badge.svg)](https://github.com/languagetool-org/dictionary-tools/actions/workflows/pytest.yml)

# Dictionary Tools
This repository contains tools for compiling and deploying dictionaries for [LanguageTool](https://languagetool.org/).

## Maintainer

The owner, maintainer, and main dev for this repository is @p-goulart. Any potential shell and perl components may be
better explained by @jaumeortola, though.

## Installation

Under construction!

## Usage

This repository should be a submodule of language-specific repositories. For example, the [Portuguese repository](https://github.com/languagetool-org/portuguese-pos-dict).

⚠️ Note that the name of this repository is in **kebab-case**, but Python modules should be imported in **snake_case**.
Therefore, when importing this as a submodule, make sure to set the path to `dict_tools`, which uses the underscore.
If you don't do this, you may fail to import it as a module.
