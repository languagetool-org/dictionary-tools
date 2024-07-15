"""Mostly written by ChatGPT plus some additional fixes from me."""
import argparse
import re
from os import path
from typing import Tuple, List

from lib.logger import LOGGER
import lib.global_dirs as gd


class CLI:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Update version in pom.xml file.')
        parser.add_argument('--pom-file', help='Path to the pom.xml file', required=False, type=str)
        parser.add_argument('--package-name', help='Name of the package to update')
        parser.add_argument('--new-version', help='New version number')
        parser.add_argument("--verbosity", type=str, choices=['debug', 'info', 'warning', 'error', 'critical'],
                            default='info', help='Verbosity level. Default is info.')
        parser.add_argument("--repo-dir", type=str, required=False)
        self.args = parser.parse_args()

    def update_pom_version(self, pom_path: str, version_tags: Tuple[str, str]):
        LOGGER.debug(f"In {pom_path}, setting {self.args.package_name}.version to {self.args.new_version}")
        new_version = self.args.new_version
        with open(pom_path, 'r') as file:
            lines = file.readlines()
        updated = False
        version_tag_open, version_tag_close = version_tags
        version_regex = re.compile(r'({0}).*?({1})'.format(re.escape(version_tag_open), re.escape(version_tag_close)))

        for i, line in enumerate(lines):
            if version_tag_open in line:
                lines[i] = lines[i] = version_regex.sub(lambda m: f"{m.group(1)}{new_version}{m.group(2)}", line)
                updated = True
                break

        # Write back to the file if updated
        if updated:
            with open(pom_path, 'w') as file:
                file.writelines(lines)
            LOGGER.info(f"Updated {self.args.package_name} version in {pom_path} to {new_version}")
        else:
            LOGGER.error(f"Package '{self.args.package_name}' not found in {pom_path}")
            exit(1)

    def pom_paths(self) -> List[Tuple[str, Tuple[str, str]]]:
        return [
            (self.args.pom_file or path.join(gd.DIRS.LT_DIR, 'pom.xml'),
             (f'<{self.args.package_name}.version>', f'</{self.args.package_name}.version>')),
            (path.join(gd.DIRS.JAVA_RESULTS_DIR, 'pom.xml'),
             ("<version>", "</version>"))
        ]

    def run(self):
        for pom_path, version_tags in self.pom_paths():
            if path.exists(pom_path):
                self.update_pom_version(pom_path, version_tags)


if __name__ == "__main__":
    cli = CLI()
    gd.initialise_dir_utils(cli.args.repo_dir)
    DIRS = gd.DIRS
    LOGGER.setLevel(cli.args.verbosity.upper())
    cli.run()
