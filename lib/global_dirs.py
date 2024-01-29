"""Singleton for DirUtils object, so we can set the directory paths once and then use them throughout the project."""
from typing import Optional

from lib.dir_utils import DirUtils

DIRS = None


def initialise_dir_utils(repo_dir: Optional[str] = None):
    global DIRS
    if DIRS is None:
        DIRS = DirUtils(repo_dir)
