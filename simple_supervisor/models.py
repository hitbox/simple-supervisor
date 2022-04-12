import enum
import subprocess

from pathlib import Path

class CommandType(enum.Enum):
    command = 'command'
    safer_command = 'safer_command'


class Command:
    """
    Hold subprocess.run arguments and options.
    """

    def __init__(
        self,
        command_args,
        cwd = None,
        capture_output = False,
        check = False,
        stdout = None,
        stderr = None,
    ):
        self.command_args = command_args
        self.cwd = cwd
        self.capture_output = capture_output
        self.check = check
        self.stdout = stdout
        self.stderr = stderr

    def resolve_cwd(self):
        if self.cwd:
            return Path(self.cwd)
        else:
            return Path.cwd()

    def run_kwargs(self):
        """
        Return keyword arguments for subprocess.run.
        """
        return dict(
            cwd = self.cwd,
            capture_output = self.capture_output,
            check = self.check,
            stdout = self.stdout,
            stderr = self.stderr,
        )

    def run(self):
        """
        Run this command returning result as configured for subprocess.run.
        """
        return subprocess.run(self.command_args, **self.run_kwargs())

    def preview(self):
        """
        Return string preview of command to run.
        """
        return self.resolve_cwd() / subprocess.list2cmdline(self.command_args)
