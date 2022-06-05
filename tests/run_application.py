"""RunApplication class helps test command-line applications with pytest."""

import os
import re
import subprocess

PYTEST_ROOT = os.path.abspath(os.curdir)


class RunApplication:
    """Run applications and return results."""

    def __init__(self, name='', command=''):
        self.name = name
        self.command = command
        self.result = None
        self.source_folder = ''

    @property
    def appcmd(self) -> str:
        """Get the application name with the command (if any) after it."""
        if self.command:
            return f'{self.name} {self.command}'
        return self.name

    @property
    def filename(self) -> str:
        """Get the path and filename of the application script being tested."""
        if self.source_folder and not self.source_folder.endswith('/'):
            self.source_folder += '/'
        return f'{self.source_folder}{self.name}'

    @property
    def returncode(self) -> int:
        """Get the return code after running the application."""
        return self.result.returncode

    @property
    def stderr(self) -> str:
        """Get the STDERR output as a single string."""
        return str(self.result.stderr, encoding='utf-8').rstrip()

    @property
    def stderrlines(self) -> str:
        """Get the STDERR output as a list of strings."""
        return str(self.result.stderr, encoding='utf-8').splitlines()

    @property
    def stdout(self) -> str:
        """Get the STDOUT output as a single string."""
        return str(self.result.stdout, encoding='utf-8').rstrip()

    @property
    def stdoutlines(self) -> str:
        """Get the STDOUT output as a list of strings."""
        return str(self.result.stdout, encoding='utf-8').splitlines()

    @staticmethod
    def joinlines(lines):
        """Join the lines into a single string."""
        return ' '.join(line.strip() for line in lines).strip()

    def stderr_findlines(self, *, start=None, stop=None):
        """Return a list of STDERR lines based on the the provided regular expressions.

        start = The first line that matches this regex will be included in the return value.
                None (the default) will start with the first line.

        stop = Lines will not be included in the return value starting with the first line
                that matches this regex will. None (the default) will return all remaining lines.
        """
        return self._findlines(self.stderrlines, start, stop)

    def stdout_findlines(self, *, start=None, stop=None):
        """Return a list of STDOUT lines based on the the provided regular expressions.

        start = The first line that matches this regex will be included in the return value.
                None (the default) will start with the first line.

        stop = Lines will not be included in the return value starting with the first line
                that matches this regex will. None (the default) will return all remaining lines.
        """
        return self._findlines(self.stdoutlines, start, stop)

    def _findlines(self, lines: list, start: str, stop: str):
        linesout = []
        if start is None:
            start_index = 0
        else:
            start_index = self._firstwith(start, lines)
        if start_index >= 0:
            if stop is None:
                stop_index = len(lines)
            else:
                stop_index = self._firstwith(stop, lines, start_index)
            if stop_index >= 0:
                linesout = lines[start_index:stop_index]
        return linesout

    @staticmethod
    def _firstwith(regex: str, lines: list, start_after: int = -1) -> int:
        for index, line in enumerate(lines):
            if index <= start_after:
                continue
            if re.search(regex, line):
                return index
        return -1

    def run(self, *args):
        """Run an application and capture output."""
        cmd = ['python', self.filename, *args]
        if self.command:
            cmd.insert(2, self.command)
        self.result = subprocess.run(cmd, cwd=PYTEST_ROOT,
                                     capture_output=True, check=False, timeout=5000)
