import codecs
import shutil
from datetime import timedelta
from os import path
from tempfile import NamedTemporaryFile
from typing import Optional

from lib.constants import LATIN_1_ENCODING
import lib.global_dirs as gd
from lib.shell_command import ShellCommand
from lib.logger import LOGGER


def compile_lt_dev():
    """Build with maven in the languagetool-dev directory."""
    LOGGER.info("Compiling LT dev...")
    wd = path.join(gd.DIRS.LT_DIR, "languagetool-dev")
    ShellCommand("mvn clean compile assembly:single", cwd=wd).run()


def compile_lt():
    """Build with maven in the languagetool-dev directory."""
    LOGGER.info("Compiling LT...")
    ShellCommand("mvn clean install -DskipTests", cwd=gd.DIRS.LT_DIR).run()


def install_dictionaries(custom_version: Optional[str]):
    """Install our dictionaries to the local ~/.m2."""
    LOGGER.info("Installing dictionaries...")
    env: dict = {}
    if custom_version is not None:
        LOGGER.info(f"Installing custom version \"{custom_version}\"")
        env['PT_DICT_VERSION'] = custom_version
    else:
        LOGGER.info(f"Installing environment-defined version \"{env['PT_DICT_VERSION']}\"")
    ShellCommand("mvn clean install", env=env, cwd=gd.DIRS.JAVA_RESULTS_DIR).run()


def convert_to_utf8(tmp_file: NamedTemporaryFile, delete_tmp: bool = False) -> NamedTemporaryFile:
    """Takes a Latin-1-encoded temp and returns another temp with the same contents but in UTF-8."""
    utf8_tmp = NamedTemporaryFile(mode='w+', encoding='utf-8', delete=delete_tmp)
    LOGGER.debug(f"Converting {tmp_file.name} into UTF-8, into {utf8_tmp.name} ...")
    with codecs.open(tmp_file.name, 'r', encoding=LATIN_1_ENCODING) as file:
        shutil.copyfileobj(file, utf8_tmp)
    utf8_tmp.seek(0)
    return utf8_tmp


def pretty_time_delta(time_delta: timedelta) -> str:
    """Taken from https://gist.github.com/thatalextaylor/7408395 and tweaked slightly."""
    seconds = int(time_delta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd%dh%dmin%ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh%dmin%ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dmin%ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)
