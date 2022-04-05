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
        capture_output = True,
        check = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
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

    def preview(self):
        """
        """
        return self.resolve_cwd() / subprocess.list2cmdline(self.command_args)
