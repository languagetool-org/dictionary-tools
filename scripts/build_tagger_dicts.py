"""This script builds the binaries for the tagger and synthesiser dictionaries. It has much less in terms of specific
logic, since most of it remains written in Perl.
"""
import argparse
import os

from dict_tools.logger import LOGGER
from dict_tools.constants import (TAGGER_BUILD_SCRIPT_PATH, FDIC_DIR, RESULT_POS_DICT_FILEPATH,
                                  SORTED_POS_DICT_FILEPATH, POS_DICT_DIFF_FILEPATH, OLD_POS_DICT_FILEPATH, REPO_DIR,
                                  TAGGER_DICT_DIR, LT_RESULTS_DIR, LT_JAR_PATH)
from dict_tools.shell_command import ShellCommand
from dict_tools.utils import compile_lt_dev, install_dictionaries
from dict_tools.variant import Variant, VARIANT_MAPPING


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


def set_shell_env() -> dict[str, str]:
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


def run_shell_script(env: dict) -> None:
    """Calls the shell script that gathers the tagger dict source files into a single TXT."""
    ShellCommand(f"bash {TAGGER_BUILD_SCRIPT_PATH}", env=env).run_with_output()


def build_pos_binary(variant: Variant) -> None:
    cmd_build = (
        f"java -cp {LT_JAR_PATH} "
        f"org.languagetool.tools.POSDictionaryBuilder "
        f"-i {RESULT_POS_DICT_FILEPATH} "
        f"-info {variant.pos_info_java_input_path()} "
        f"-o {variant.pos_dict_java_output_path()}"
    )
    ShellCommand(cmd_build).run()
    variant.copy_pos_info()


def build_synth_binary(variant: Variant) -> None:
    cmd_build = (
        f"java -cp {LT_JAR_PATH} "
        f"org.languagetool.tools.SynthDictionaryBuilder "
        f"-i {RESULT_POS_DICT_FILEPATH} "
        f"-info {variant.synth_info_java_input_path()} "
        f"-o {variant.synth_dict_java_output_path()}"
    )
    ShellCommand(cmd_build).run()
    variant.copy_synth_info()
    variant.rename_synth_tag_files()


def main():
    cli = CLI()
    LOGGER.setLevel(cli.args.verbosity.upper())
    FORCE_INSTALL = cli.args.force_install
    FORCE_COMPILE = cli.args.no_force_compile
    CUSTOM_INSTALL_VERSION = cli.args.install_version
    DIC_VARIANTS = VARIANT_MAPPING[cli.args.language]
    SHELL_ENV = set_shell_env()
    if FORCE_COMPILE:
        compile_lt_dev()
    for variant in DIC_VARIANTS:
        run_shell_script(SHELL_ENV)
        build_pos_binary(variant)
        build_synth_binary(variant)
    if FORCE_INSTALL:
        install_dictionaries(custom_version=CUSTOM_INSTALL_VERSION)


if __name__ == "__main__":
    main()
