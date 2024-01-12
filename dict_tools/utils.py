from os import chdir, path
from typing import Optional

from dict_tools.constants import REPO_DIR, LT_DIR, JAVA_RESULTS_DIR
from dict_tools.shell_command import ShellCommand
from dict_tools.logger import LOGGER


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
