"""This script builds the binaries for the tagger and synthesiser dictionaries. It has much less in terms of specific
logic, since most of it remains written in Perl.
"""
import argparse
import os
from datetime import datetime

from lib.languagetool_utils import LanguageToolUtils
from lib.logger import LOGGER
from lib.constants import (TAGGER_BUILD_SCRIPT_PATH, FDIC_DIR, RESULT_POS_DICT_FILEPATH,
                           SORTED_POS_DICT_FILEPATH, POS_DICT_DIFF_FILEPATH, OLD_POS_DICT_FILEPATH, REPO_DIR,
                           TAGGER_DICT_DIR, LT_RESULTS_DIR)
from lib.shell_command import ShellCommand
from lib.utils import compile_lt_dev, install_dictionaries, pretty_time_delta
from lib.variant import Variant


class CLI:
    prog_name = "poetry run python build_tagger_dicts.py"
    epilogue = "In case of problems when running this script, address a Github issue to the repository maintainer."
    description = "This script takes PoS tagger data for Portuguese and builds Morfologik-format binary files."

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description=self.description,
            epilog=self.epilogue,
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.parser.add_argument('--language', type=str, help='Language code (e.g. pt-BR, en-US).',
                                 choices=Variant.LANG_CODES.keys(), required=True)
        self.parser.add_argument('--no-force-compile', action='store_false',
                                 help='Do not force LT compilation.')
        self.parser.add_argument('--force-install', action='store_true',
                                 help='Install resulting binaries to local ~/.m2.')
        self.parser.add_argument("--install-version", type=str, required=False,
                                 help="Custom version for the dictionary installation (overrides $PT_DICT_VERSION).")
        self.parser.add_argument('--verbosity', type=str, choices=['debug', 'info', 'warning', 'error', 'critical'],
                                 default='info', help='Verbosity level. Default is info.')
        self.args = self.parser.parse_args()


def set_shell_env():
    custom_env = {
        'REPO_DIR': REPO_DIR,
        'DATA_SRC_DIR': TAGGER_DICT_DIR,
        'RESULTS_DIR': LT_RESULTS_DIR,
        'FDIC_DIR': FDIC_DIR,
        'RESULT_DICT_FILEPATH': RESULT_POS_DICT_FILEPATH,
        'SORTED_DICT_FILEPATH': SORTED_POS_DICT_FILEPATH,
        'DICT_DIFF_FILEPATH': POS_DICT_DIFF_FILEPATH,
        'OLD_DICT_FILEPATH': OLD_POS_DICT_FILEPATH
    }
    return {**os.environ, **custom_env}


def run_shell_script() -> None:
    """Calls the shell script that gathers the tagger dict source files into a single TXT."""
    ShellCommand(f"bash {TAGGER_BUILD_SCRIPT_PATH}", env=SHELL_ENV).run_with_output()


def main():
    start_time = datetime.now()
    LOGGER.debug(f"Started at {start_time.strftime('%r')}")
    if FORCE_COMPILE:
        compile_lt_dev()
    run_shell_script()
    lt = LanguageToolUtils(LANGUAGE)
    lt.build_pos_binary()
    lt.build_synth_binary()
    if FORCE_INSTALL:
        install_dictionaries(custom_version=CUSTOM_INSTALL_VERSION)
    end_time = datetime.now()
    LOGGER.debug(f"Finished at {end_time.strftime('%r')}. "
                 f"Total time elapsed: {pretty_time_delta(end_time - start_time)}.")


if __name__ == "__main__":
    cli = CLI()
    LOGGER.setLevel(cli.args.verbosity.upper())
    FORCE_INSTALL = cli.args.force_install
    FORCE_COMPILE = cli.args.no_force_compile
    CUSTOM_INSTALL_VERSION = cli.args.install_version
    LANGUAGE = Variant(cli.args.language)
    SHELL_ENV = set_shell_env()
    main()
