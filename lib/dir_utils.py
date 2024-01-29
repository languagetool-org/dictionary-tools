import pathlib
from os import path, environ, getcwd
from typing import Optional

from lib.constants import LT_VER


class DirUtils:
    def __init__(self, repo_dir: Optional[str] = None):
        self.REPO_DIR: str = repo_dir or getcwd()
        # LT home is read as an environment variable, but if it's not set, we use the default path of the parent
        # repo's parent
        self.LT_HOME = environ.get('LT_HOME')
        self.LT_DIR = path.join(pathlib.Path(self.REPO_DIR).parent,
                                "languagetool") if self.LT_HOME is None else self.LT_HOME

        # These are paths to source data, which is obviously not included in this repo
        self.DATA_DIR = path.join(self.REPO_DIR, 'data')
        self.SPELLING_DICT_DIR = path.join(self.DATA_DIR, "spelling-dict")
        self.HUNSPELL_DIR = path.join(self.SPELLING_DICT_DIR, "hunspell")
        self.TAGGER_DICT_DIR = path.join(self.DATA_DIR, "src-dict")
        self.COMPOUNDS_DIR = path.join(self.HUNSPELL_DIR, 'compounds')  # potentially used only Portuguese

        # TODO: this *may* at some point be moved here, but that depends on how much work it will be to adapt the
        #  shell/perl; Tagger scripts paths
        self.TAGGER_SCRIPTS_DIR = path.join(self.REPO_DIR, "pos_tagger_scripts")
        self.TAGGER_BUILD_SCRIPT_PATH = path.join(self.TAGGER_SCRIPTS_DIR, "build-lt.sh")
        self.FDIC_DIR = path.join(self.TAGGER_SCRIPTS_DIR, "fdic-to-lt")

        # Output paths – these are paths to *pre-compilation* data, i.e. plaintext files used by the LT build process to
        # generate the compiled Morfologik data.
        self.RESULTS_DIR = path.join(self.REPO_DIR, 'results')
        self.JAVA_RESULTS_DIR = path.join(self.RESULTS_DIR, 'java-lt')
        self.LT_RESULTS_DIR = path.join(self.RESULTS_DIR, 'lt')
        self.RESULT_POS_DICT_FILEPATH = path.join(self.LT_RESULTS_DIR, "dict.txt")
        self.SORTED_POS_DICT_FILEPATH = path.join(self.LT_RESULTS_DIR, "dict_sorted.txt")
        self.POS_DICT_DIFF_FILEPATH = path.join(self.LT_RESULTS_DIR, "dict.diff")
        self.OLD_POS_DICT_FILEPATH = path.join(self.LT_RESULTS_DIR, "dict.old")

        # Paths to Jar files. These are the ones we will use to compile the Morfologik-format dictionaries to be used
        # by LT.
        self.LT_JAR_PATH = path.join(self.LT_DIR, 'languagetool-standalone', 'target', f"LanguageTool-{LT_VER}",
                                     f"LanguageTool-{LT_VER}",
                                     'languagetool.jar')
        self.LT_JAR_WITH_DEPS_PATH = path.join(self.LT_DIR, "languagetool-dev", "target",
                                               f"languagetool-dev-{LT_VER}-jar-with-dependencies.jar")
