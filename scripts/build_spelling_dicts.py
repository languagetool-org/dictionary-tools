"""This was translated from shell to python iteratively and interactively using ChatGPT 4."""
import argparse
from datetime import datetime
from typing import List
import concurrent.futures
from tempfile import NamedTemporaryFile
from os import path

from lib.dic_chunk import DicChunk
import lib.global_dirs as gd
from lib.logger import LOGGER
from lib.utils import compile_lt_dev, install_dictionaries, convert_to_utf8, pretty_time_delta, compile_lt
from lib.variant import Variant, VARIANT_MAPPING
from lib.languagetool_utils import LanguageToolUtils as LtUtils


class CLI:
    prog_name = "poetry run python build_spelling_dicts.py"
    epilogue = "In case of problems when running this script, address a Github issue to the repository maintainer."
    description = ("This script takes Hunspell data for Portuguese and builds Morfologik-format binary files to be used"
                   "by LT's Java speller rule. It does so in four steps:\n\n"
                   "1. split the plaintext .dic files into chunks to be run in parallel;\n"
                   "2. run unmunch on each chunk, thus expanding all word forms therein;\n"
                   "3. run LT's word tokenisation on the unmunched word forms, thus splitting them;\n"
                   "4. merge all the unmunched and tokenised forms, add a list of compounds and then use LT to compile"
                   "the files into the appropriate format.\n\n"
                   "At the end of the execution, the script may also automatically install the binary files locally so"
                   "you can test them on a local instance of LT.")

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description=self.description,
            epilog=self.epilogue,
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.parser.add_argument('--language', type=str, help='Language code (e.g. pt-BR, en-US).',
                                 choices=Variant.LANG_CODES.keys(), required=True)
        self.parser.add_argument('--tmp-dir', default="tmp", required=False,
                                 help='Temporary directory for processing. Default is the "tmp" directory inside '
                                      'DICT_DIR.')
        self.parser.add_argument('--delete-tmp', action='store_true',
                                 help='Delete temporary files after processing. Default is False.')
        self.parser.add_argument('--sample-size', type=int, default=-1,
                                 help='Size of the sample. Use negative for no sample. Default is -1.')
        self.parser.add_argument('--chunk-size', type=int, default=20000,
                                 help='Size of the chunks for splitting. Default is 20000.')
        self.parser.add_argument('--max-threads', type=int, default=8,
                                 help='Maximum number of threads to use. Default is 8.')
        self.parser.add_argument('--no-force-compile', action='store_false',
                                 help='Do NOT force LT compilation.')
        self.parser.add_argument('--force-install', action='store_true',
                                 help='Install resulting binaries to local ~/.m2.')
        self.parser.add_argument("--install-version", type=str, required=False,
                                 help="Custom version for the dictionary installation (overrides $PT_DICT_VERSION).")
        self.parser.add_argument('--verbosity', type=str, choices=['debug', 'info', 'warning', 'error', 'critical'],
                                 default='info', help='Verbosity level. Default is info.')
        self.parser.add_argument("--repo-dir", type=str, required=False)
        self.args = self.parser.parse_args()


def process_variant(variant: Variant, dic_chunk: DicChunk) -> tuple[Variant, NamedTemporaryFile]:
    """For each file, runs unmunch, tokenisation (if applicable), and returns a tuple of the Variant and temp file."""
    unmunched_file = dic_chunk.unmunch(variant.aff(), DELETE_TMP)
    if dic_chunk.compounds:
        processed_file = convert_to_utf8(unmunched_file, DELETE_TMP)
    else:
        processed_file = LtUtils(variant, DELETE_TMP).tokenise(unmunched_file)
    return variant, processed_file


def main():
    start_time = datetime.now()
    LOGGER.debug(f"Started at {start_time.strftime('%r')}")
    LOGGER.debug(
        f"Options used:\n"
        f"TMP_DIR: {TMP_DIR}\n"
        f"DELETE_TMP: {DELETE_TMP}\n"
        f"SAMPLE_SIZE: {SAMPLE_SIZE}\n"
        f"CHUNK_SIZE: {CHUNK_SIZE}\n"
        f"MAX_THREADS: {MAX_THREADS}\n"
        f"FORCE_COMPILE: {FORCE_COMPILE}\n"
        f"FORCE_INSTALL: {FORCE_INSTALL}\n"
        f"CUSTOM_INSTALL_VERSION: {CUSTOM_INSTALL_VERSION}\n"
        f"DIC_VARIANTS: {DIC_VARIANTS}\n"
    )
    # We might consider *always* compiling, since the spelling dicts depends on the tagger dicts having been *installed*
    # and compiled with LT. The reason we need to also re-build LT is that we need to make sure that OUR tagger dicts
    # are used by the WordTokenizer.
    if FORCE_COMPILE:
        compile_lt()
        compile_lt_dev()
    tasks = []
    processed_files: dict[str: List[NamedTemporaryFile]] = {}
    # TODO: PORTUGUESE – at some point we need to manage the pre and post-agreement distinction here
    # the whole 'dict_variant' will need to go, and we will just merge all the unmunched files into one big one
    # and then split them based on the dialectal and pre/post agreement alternation files
    for variant in DIC_VARIANTS:
        processed_files[variant] = []
        dic_chunks: List[DicChunk] = DicChunk.from_hunspell_dic(variant, CHUNK_SIZE, TMP_DIR, SAMPLE_SIZE)
        dic_chunks.extend(DicChunk.from_hunspell_dic(variant, CHUNK_SIZE, TMP_DIR, SAMPLE_SIZE, compounds=True))
        for chunk in dic_chunks:
            tasks.append((variant, chunk))
    LOGGER.info("Starting unmunching and tokenisation process...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        tmp_files = executor.map(lambda task: process_variant(task[0], task[1]), tasks)
        for variant, file in tmp_files:
            processed_files[variant].append(file)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(lambda var: LtUtils(var, DELETE_TMP).build_spelling_binary(processed_files[var]), DIC_VARIANTS)
    for file_list in processed_files.values():
        for file in file_list:
            file.close()
    if FORCE_INSTALL:
        install_dictionaries(CUSTOM_INSTALL_VERSION)
    end_time = datetime.now()
    LOGGER.debug(f"Finished at {end_time.strftime('%r')}. "
                 f"Total time elapsed: {pretty_time_delta(end_time - start_time)}.")


if __name__ == "__main__":
    cli = CLI()
    args = cli.args
    LOGGER.setLevel(args.verbosity.upper())
    gd.initialise_dir_utils(args.repo_dir)
    DIRS = gd.DIRS
    TMP_DIR = path.join(DIRS.SPELLING_DICT_DIR, args.tmp_dir)
    DELETE_TMP = args.delete_tmp
    SAMPLE_SIZE = args.sample_size
    CHUNK_SIZE = args.chunk_size
    MAX_THREADS = args.max_threads
    FORCE_COMPILE = args.no_force_compile
    FORCE_INSTALL = args.force_install
    CUSTOM_INSTALL_VERSION = args.install_version
    DIC_VARIANTS = VARIANT_MAPPING.get(args.language)
    main()
