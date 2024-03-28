import pytest

from lib.shell_command import ShellCommand, ShellCommandException, LOGGER


class TestShellCommand:
    """Test the ShellCommand class."""
    def test_run(self):
        assert ShellCommand("echo 'Hello, World!'").run() == b"Hello, World!\n"

    def test_run_with_input(self):
        assert ShellCommand("tr 'o' 'a'").run_with_input("foo") == "faa"

    def test_run_with_output(self, caplog):
        """Test the run_with_output method: shell command output is redirected to the logger on the debug level."""
        LOGGER.setLevel("DEBUG")
        ShellCommand("expr 2 + 2").run_with_output()
        assert caplog.text == ('DEBUG    dictionary_tools:shell_command.py:64 Running command: expr 2 + 2\n'
                               'DEBUG    dictionary_tools:shell_command.py:71 4\n') != '4'
        LOGGER.setLevel("FATAL")

    def test_run_with_not_found_error(self):
        with pytest.raises(ShellCommandException):
            ShellCommand("_echo_bad_command_will_not_work_").run()

    def test_run_with_other_error(self):
        with pytest.raises(ShellCommandException):
            ShellCommand("ls --invalid-option").run_with_output()
