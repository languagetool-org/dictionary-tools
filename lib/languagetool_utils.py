import re
from tempfile import NamedTemporaryFile
from typing import List

from lib.constants import LATIN_1_ENCODING, LT_VER
import lib.global_dirs as gd
from lib.logger import LOGGER
from lib.shell_command import ShellCommand
from lib.variant import Variant


class LanguageToolUtils:
    def __init__(self, variant: Variant, delete_tmp: bool = False):
        self.variant = variant
        self.delete_tmp = delete_tmp

    def tokenise(self, unmunched_file: NamedTemporaryFile) -> NamedTemporaryFile:
        """Tokenise each line of an unmunched file, write it to another temp file and return it.

        The written data looks weird, since the output of the LT word tokeniser inserts newlines between tokens.
        Original line after unmunch:
           "far-se-á"
        Lines after tokenisation:
            "far"
            ""
            "se"
            ""
            "á"
        This may look iffy, but later in the process we will sort and dedupe these files, so don't panic.

        Args:
            unmunched_file: the NamedTemporaryFile object for the unmunched file we'll be tokenising

        Returns:
            a NamedTemporaryFile with the result of tokenisation written to it; note this is a UTF-8-encoded file; it is
            not at this stage that we move from latin-1 encoding to UTF-8.
        """
        chunk_pattern = re.compile("[a-z]{2}_[A-Z]{2}(?:_[a-zA-Z0-9]+)?_chunk\\d+")
        prefix = chunk_pattern.findall(unmunched_file.name.split('/')[-1])[0] + "_tokenised_"
        tokenised_tmp = NamedTemporaryFile(delete=self.delete_tmp, mode='w', prefix=prefix)
        LOGGER.debug(f"Tokenising {unmunched_file.name} into {tokenised_tmp.name} ...")
        tokenise_cmd = (
            f"java -cp {gd.DIRS.LT_JAR_PATH}:"
            f"{gd.DIRS.LT_DIR}/languagetool-dev/target/languagetool-dev-{LT_VER}-jar-with-dependencies.jar "
            f"org.languagetool.dev.archive.WordTokenizer {self.variant.lang}"
        )
        with open(unmunched_file.name, 'r', encoding=LATIN_1_ENCODING) as u:
            unmunched_str = u.read()
        unmunched_file.close()
        tokenisation_result = ShellCommand(tokenise_cmd).run_with_input(unmunched_str)
        tokenised_tmp.write(tokenisation_result)
        tokenised_tmp.flush()
        LOGGER.debug(f"Done tokenising {unmunched_file.name}!")
        return tokenised_tmp

    def build_spelling_binary(self, tokenised_temps: List[NamedTemporaryFile]) -> None:
        """Merge many unmunched and tokenised files into *one* plaintext file and used that to build a Morfologik
        SPELLING dictionary.

        The files must be merged and converted into UTF-8 before we can do anything with them. Once we have a single
        'master' temp file per variant, we can pass that file as an input parameter to the Java tool that builds
        spelling dictionaries.

        If the shell command is successful, we will have a new output file saved to the appropriate result directory.
        This will be a binary file ready to be released and used by Morfologik.

        Returns:
            None
        """
        LOGGER.info(f"Building spelling binary for {self.variant}...")
        megatemp = NamedTemporaryFile(delete=self.delete_tmp, mode='w',
                                      encoding='utf-8')  # Open the file with UTF-8 encoding
        lines = set()
        for tmp in tokenised_temps:
            with open(tmp.name, 'r', encoding='utf-8') as t:
                lines.update(t.read().split("\n"))
        megatemp.write("\n".join(sorted(lines)))
        LOGGER.debug(f"Found {len(lines)} unique unmunched and tokenised forms for {self.variant}.")
        cmd_build = (
            f"java -cp {gd.DIRS.LT_JAR_PATH} "
            f"org.languagetool.tools.SpellDictionaryBuilder "
            f"-i {megatemp.name} "
            f"-info {self.variant.info('source')} "
            f"-freq {self.variant.freq()} "
            f"-o {self.variant.dict()}"
        )
        ShellCommand(cmd_build).run()
        LOGGER.info(f"Done compiling {self.variant} spelling dictionary!")
        self.variant.copy_spell_info()
        megatemp.close()

    def build_pos_binary(self) -> None:
        LOGGER.info(f"Building part-of-speech binary for {self.variant}...")
        cmd_build = (
            f"java -cp {gd.DIRS.LT_JAR_PATH} "
            f"org.languagetool.tools.POSDictionaryBuilder "
            f"-i {gd.DIRS.RESULT_POS_DICT_FILEPATH} "
            f"-info {self.variant.pos_info_java_input_path()} "
            f"-o {self.variant.pos_dict_java_output_path()}"
        )
        ShellCommand(cmd_build).run()
        LOGGER.info(f"Done compiling {self.variant} part-of-speech dictionary!")
        self.variant.copy_pos_info()

    def build_synth_binary(self) -> None:
        LOGGER.info(f"Building synthesiser binary for {self.variant}...")
        cmd_build = (
            f"java -cp {gd.DIRS.LT_JAR_PATH} "
            f"org.languagetool.tools.SynthDictionaryBuilder "
            f"-i {gd.DIRS.RESULT_POS_DICT_FILEPATH} "
            f"-info {self.variant.synth_info_java_input_path()} "
            f"-o {self.variant.synth_dict_java_output_path()}"
        )
        ShellCommand(cmd_build).run()
        LOGGER.info(f"Done compiling {self.variant} synthesiser dictionary!")
        self.variant.copy_synth_info()
        self.variant.rename_synth_tag_files()

    def dump_dictionary(self) -> None:
        LOGGER.info(f"Dumping dictionary for {self.variant}...")
        cmd_dump = (
            f"java -cp {gd.DIRS.LT_JAR_PATH} "
            f"org.languagetool.tools.DictionaryExporter "
            f"-i {self.variant.pos_dict_java_output_path()} "
            f"-info {self.variant.pos_info_java_input_path()} "
            f"-o {self.variant.dump_dict_java_output_path()}"
        )
        ShellCommand(cmd_dump).run()
        LOGGER.info(f"Done dumping {self.variant} dictionary!")
