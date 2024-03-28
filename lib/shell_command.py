import os
import shlex
import subprocess
from typing import AnyStr

from lib.logger import LOGGER


class ShellCommandException(Exception):
    """An exception raised when a Java command fails."""
    def __init__(self, return_code: int, stderr: AnyStr = None):
        self.message = f"Command failed with error code {return_code}: {stderr}"
        LOGGER.error(self.message)
        super().__init__(self, self.message)


class ShellCommand:
    """A class for executing Java commands."""
    def __init__(self, command_str: str, env: dict = None, cwd: str = '.'):
        self.command_str = command_str
        self.split_cmd = shlex.split(self.command_str)
        self.env: dict = {**os.environ}
        self.cwd = cwd
        if env is not None:
            self.env.update(env)

    @staticmethod
    def check_status(return_code: int, stderr: AnyStr) -> None:
        """Check if the return code of a command is 0 and return the stderr if it is not."""
        if return_code != 0:
            raise ShellCommandException(return_code, stderr)
        return None

    def _popen(self, text: bool = False) -> subprocess.Popen:
        try:
            return subprocess.Popen(self.split_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=text, env=self.env, cwd=self.cwd)
        except FileNotFoundError:
            raise ShellCommandException(255, "Command or file not found.")

    def _run(self) -> subprocess.run:
        try:
            return subprocess.run(self.split_cmd, capture_output=True, env=self.env, cwd=self.cwd)
        except FileNotFoundError:
            raise ShellCommandException(255, "Command or file not found.")

    def run(self) -> bytes:
        """Execute the shell command and return its output as bytes."""
        LOGGER.debug(f"Running command: {self.command_str}")
        result = self._run()
        self.check_status(result.returncode, result.stderr)
        return result.stdout

    def run_with_input(self, input_data: str) -> str:
        """Execute the shell command with the provided input and return its output."""
        LOGGER.debug(f"Running command with piped stdin: {self.command_str}")
        process = self._popen(text=True)
        stdout_data, stderr_data = process.communicate(input=input_data)
        self.check_status(process.returncode, stderr_data)
        return stdout_data

    def run_with_output(self) -> None:
        """Execute the given shell command and print its output in real time."""
        LOGGER.debug(f"Running command: {self.command_str}")
        process = self._popen()
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                LOGGER.debug(output.decode().strip())
            err = process.stderr.readline()
            if err:
                LOGGER.warn(err.decode().strip())
        rc = process.poll()
        remaining_err = process.stderr.read()
        if remaining_err:
            LOGGER.warn(remaining_err.decode().strip())
        self.check_status(rc, process.stderr.read())
