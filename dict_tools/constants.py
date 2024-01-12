from os import path, environ
import pathlib

LT_VER = "6.4-SNAPSHOT"
LATIN_1_ENCODING = 'ISO-8859-1'

# Paths
REPO_DIR = pathlib.Path(path.dirname(path.abspath(__file__))).parent
LT_HOME = environ.get('LT_HOME')
LT_DIR = path.join(pathlib.Path(REPO_DIR).parent, "languagetool") if LT_HOME is None else LT_HOME
DATA_DIR = path.join(REPO_DIR, 'data')
SPELLING_DICT_DIR = path.join(DATA_DIR, "spelling-dict")
HUNSPELL_DIR = path.join(SPELLING_DICT_DIR, "hunspell")
TAGGER_DICT_DIR = path.join(DATA_DIR, "src-dict")
TAGGER_SCRIPTS_DIR = path.join(REPO_DIR, "pos_tagger_scripts")
TAGGER_BUILD_SCRIPT_PATH = path.join(TAGGER_SCRIPTS_DIR, "build-lt.sh")

COMPOUNDS_DIR = path.join(HUNSPELL_DIR, 'compounds')

RESULTS_DIR = path.join(REPO_DIR, 'results')
JAVA_RESULTS_DIR = path.join(RESULTS_DIR, 'java-lt')
LT_RESULTS_DIR = path.join(RESULTS_DIR, 'lt')
FDIC_DIR = path.join(TAGGER_SCRIPTS_DIR, "fdic-to-lt")
RESULT_POS_DICT_FILEPATH = path.join(LT_RESULTS_DIR, "dict.txt")
SORTED_POS_DICT_FILEPATH = path.join(LT_RESULTS_DIR, "dict_sorted.txt")
POS_DICT_DIFF_FILEPATH = path.join(LT_RESULTS_DIR, "dict.diff")
OLD_POS_DICT_FILEPATH = path.join(LT_RESULTS_DIR, "dict.old")

LT_JAR_PATH = path.join(LT_DIR, 'languagetool-standalone', 'target', f"LanguageTool-{LT_VER}", f"LanguageTool-{LT_VER}",
                        'languagetool.jar')
LT_JAR_WITH_DEPS_PATH = path.join(LT_DIR, "languagetool-dev", "target",
                                  f"languagetool-dev-{LT_VER}-jar-with-dependencies.jar")

