"""Mostly written by ChatGPT plus some additional fixes from me."""
import argparse
import re

from lib.logger import LOGGER
from lib.constants import LT_HOME


class CLI:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Update version in pom.xml file.')
        parser.add_argument('--pom-file', help='Path to the pom.xml file', default=f'{LT_HOME}/pom.xml')
        parser.add_argument('--package-name', help='Name of the package to update')
        parser.add_argument('--new-version', help='New version number')
        parser.add_argument("--verbosity", type=str, choices=['debug', 'info', 'warning', 'error', 'critical'],
                            default='info', help='Verbosity level. Default is info.')
        self.args = parser.parse_args()

    def update_pom_version(self):
        LOGGER.debug(f"In {self.args.pom_file}, setting {self.args.package_name}.version to {self.args.new_version}")
        file_path = self.args.pom_file
        package_name = self.args.package_name
        new_version = self.args.new_version
        with open(file_path, 'r') as file:
            lines = file.readlines()
        updated = False
        version_tag = f'<{package_name}.version>'
        version_tag_close = f'</{package_name}.version>'
        version_regex = re.compile(r'({0}).*?({1})'.format(re.escape(version_tag), re.escape(version_tag_close)))

        for i, line in enumerate(lines):
            if version_tag in line:
                lines[i] = version_regex.sub(r'\1' + new_version + r'\2', line)
                updated = True
                break

        # Write back to the file if updated
        if updated:
            with open(file_path, 'w') as file:
                file.writelines(lines)
            LOGGER.info(f"Updated {package_name} version in {file_path} to {new_version}")
        else:
            LOGGER.error(f"Package '{package_name}' not found in {file_path}")
            exit(1)

    def run(self):
        self.update_pom_version()


if __name__ == "__main__":
    cli = CLI()
    LOGGER.setLevel(cli.args.verbosity.upper())
    cli.run()
