import codecs
import shutil
from os import chdir, path
from tempfile import NamedTemporaryFile
from typing import Optional

from lib.constants import REPO_DIR, LT_DIR, JAVA_RESULTS_DIR, LATIN_1_ENCODING
from lib.shell_command import ShellCommand
from lib.logger import LOGGER


def compile_lt_dev():
    """Build with maven in the languagetool-dev directory."""
    LOGGER.info("Compiling LT dev...")
    chdir(path.join(LT_DIR, "languagetool-dev"))
    ShellCommand("mvn clean compile assembly:single").run()
    chdir(REPO_DIR)  # Go back to the repo directory


def install_dictionaries(custom_version: Optional[str]):
    """Install our dictionaries to the local ~/.m2."""
    LOGGER.info("Installing dictionaries...")
    chdir(JAVA_RESULTS_DIR)
    env: dict = {}
    if custom_version is not None:
        LOGGER.info(f"Installing custom version \"{custom_version}\"")
        env['PT_DICT_VERSION'] = custom_version
    else:
        LOGGER.info(f"Installing environment-defined version \"{env['PT_DICT_VERSION']}\"")
    ShellCommand("mvn clean install", env=env).run()
    chdir(REPO_DIR)  # Go back to the repo directory


def convert_to_utf8(tmp_file: NamedTemporaryFile, delete_tmp: bool = False) -> NamedTemporaryFile:
    """Takes a Latin-1-encoded temp and returns another temp with the same contents but in UTF-8."""
    utf8_tmp = NamedTemporaryFile(mode='w+', encoding='utf-8', delete=delete_tmp)
    LOGGER.debug(f"Converting {tmp_file.name} into UTF-8, into {utf8_tmp.name} ...")
    with codecs.open(tmp_file.name, 'r', encoding=LATIN_1_ENCODING) as file:
        shutil.copyfileobj(file, utf8_tmp)
    utf8_tmp.seek(0)
    return utf8_tmp
