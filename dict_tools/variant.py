import shutil
from os import path
from typing import Literal

from dict_tools.constants import HUNSPELL_DIR, SPELLING_DICT_DIR, COMPOUNDS_DIR, JAVA_RESULTS_DIR, TAGGER_DICT_DIR


class Variant:
    """Defines a single variant of any language.

    Attributes:
        hyphenated: the xx-XX code of the variant, with an optional "-xx" at the end for orthographic agreement.
        underscored: the underscored code of the variant, i.e. xx_XX (used for Hunspell files)
        lang: just the language, i.e. 'pt'
        country: just the country, e.g. 'BR'
        agreement: the orthographic agreement; an arbitrary string (e.g. for Portuguese, '45' or '90');
        pretty: the pretty (i.e. English) name of the language, e.g. 'Portuguese'
    """

    LANG_CODES = {'pt': 'Portuguese', 'nl': 'Dutch', 'de': 'German', 'fr': 'French', 'es': 'Spanish', 'en': 'English'}

    def __init__(self, locale_code: str):
        parsed = locale_code.split('-')
        self.lang = parsed[0]
        self.country = parsed[1]
        self.agreement = parsed[2] if len(parsed) > 2 else None
        self.pretty = self.LANG_CODES.get(self.lang)
        self.hyphenated = locale_code
        self.underscored = locale_code.replace('-', '_')

    def __str__(self) -> str:
        return self.hyphenated

    def aff(self) -> str:
        return path.join(HUNSPELL_DIR, f"{self.underscored}.aff")

    def dic(self) -> str:
        """Path to the plaintext Hunspell file."""
        return path.join(HUNSPELL_DIR, f"{self.underscored}.dic")

    def dict(self) -> str:
        """Path to the BINARY."""
        return path.join(self.spelling_output_dir(), f"{self.hyphenated}.dict")

    def info(self, directory: Literal['source', 'target']) -> str:
        """The path to the info file can be in the source (current repo) or destination (the java src)."""
        if directory == 'source':
            directory = SPELLING_DICT_DIR
        elif directory == 'target':
            directory = self.spelling_output_dir()
        return path.join(directory, f"{self.hyphenated}.info")

    def compounds(self) -> str:
        return path.join(COMPOUNDS_DIR, f"{self.underscored}.dic")

    def freq(self) -> str:
        return path.join(SPELLING_DICT_DIR, f"{self.lang}_{self.country}_wordlist.xml")

    def java_output_dir(self) -> str:
        return path.join(JAVA_RESULTS_DIR, "src/main/resources/org/languagetool/resource", self.lang)

    def spelling_output_dir(self) -> str:
        return path.join(self.java_output_dir(), "spelling")

    def pos_dict_java_output_path(self) -> str:
        return path.join(self.java_output_dir(), f"{self.pretty.lower()}.dict")

    def pos_info_java_output_path(self) -> str:
        return path.join(self.java_output_dir(), f"{self.pretty.lower()}.info")

    def synth_dict_java_output_path(self) -> str:
        return path.join(self.java_output_dir(), f"{self.pretty.lower()}_synth.dict")

    def synth_info_java_output_path(self) -> str:
        return path.join(self.java_output_dir(), f"{self.pretty.lower()}_synth.info")

    def pos_info_java_input_path(self) -> str:
        return path.join(TAGGER_DICT_DIR, f"{self.pretty.lower()}.info")

    def synth_info_java_input_path(self) -> str:
        return path.join(TAGGER_DICT_DIR, f"{self.pretty.lower()}_synth.info")

    def copy_pos_info(self) -> None:
        shutil.copy(self.pos_info_java_input_path(), self.pos_info_java_output_path())

    def copy_synth_info(self) -> None:
        shutil.copy(self.synth_info_java_input_path(), self.synth_info_java_output_path())

    def rename_synth_tag_files(self) -> None:
        shutil.move(path.join(self.java_output_dir(), f"{self.pretty.lower()}_synth.dict_tags.txt"),
                    path.join(self.java_output_dir(), f"{self.pretty.lower()}_tags.txt"))

    def copy_spell_info(self) -> None:
        return shutil.copy(self.info('source'), self.info('target'))


# Portuguese
PT_BR = Variant('pt-BR')
PT_PT_45 = Variant('pt-PT-45')
PT_PT_90 = Variant('pt-PT-90')
# Dutch
NL_NL = Variant('nl-NL')
# German
DE_DE = Variant('de-DE')
# French
FR_FR = Variant('fr-FR')
# English
EN_GB = Variant('en-GB')
EN_US = Variant('en-US')
# Spanish
ES_ES = Variant('es-ES')

VARIANT_MAPPING = {
    'pt': [PT_BR, PT_PT_45, PT_PT_90],
    'nl': [NL_NL],
    'de': [DE_DE],
    'fr': [FR_FR],
    'es': [ES_ES],
    'en': [EN_GB, EN_US],
}
