import os
import pty
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
from django.test import TestCase
from shellingham import detect_shell

from django_typer import get_command
from django_typer.management.commands.shellcompletion import Command as ShellCompletion
from django_typer.tests.polls.models import Question as Poll
from django_typer.tests.test_app.models import ShellCompleteTester

default_shell = None

try:
    default_shell = detect_shell()[0]
except Exception:
    pass


def read_all_from_fd_with_timeout(fd, timeout):
    all_data = bytearray()
    start_time = time.time()

    while True:
        # Calculate remaining time
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 0:
            break  # Timeout reached

        # Wait until the file descriptor is ready or the timeout is reached
        rlist, _, _ = select.select([fd], [], [], remaining_time)
        if not rlist:
            break  # Timeout reached

        # Read available data
        data = os.read(fd, 1024)
        if not data:
            break  # End of file reached
        all_data.extend(data)

    return bytes(all_data).decode()


@pytest.mark.skipif(default_shell is None, reason="shellingham failed to detect shell")
class DefaultCompleteTestCase(TestCase):

    shell = None
    manage_script = "manage.py"
    launch_script = "./manage.py"

    @property
    def interactive_opt(self):
        # currently all supported shells support -i for interactive mode
        # this includes zsh, bash, fish and powershell
        return "-i"

    @property
    def command(self) -> ShellCompletion:
        return get_command("shellcompletion")

    def setUp(self):
        self.remove()
        super().setUp()

    def tearDown(self):
        self.remove()
        super().tearDown()

    def verify_install(self, script=manage_script):
        pass

    def verify_remove(self, script=manage_script):
        pass

    def install(self, script=manage_script):
        kwargs = {}
        if self.shell:
            kwargs["shell"] = self.shell
        if script:
            kwargs["manage_script"] = script
        self.command.install(**kwargs)
        self.verify_install(script=script)

    def remove(self, script=manage_script):
        kwargs = {}
        if self.shell:
            kwargs["shell"] = self.shell
        if script:
            kwargs["manage_script"] = script
        self.command.remove(**kwargs)
        self.verify_remove(script=script)

    def set_environment(self, fd):
        os.write(fd, f"PATH={Path(sys.executable).parent}:$PATH\n".encode())
        os.write(
            fd,
            f'DJANGO_SETTINGS_MODULE={os.environ["DJANGO_SETTINGS_MODULE"]}\n'.encode(),
        )

    def get_completions(self, *cmds: str) -> list[str]:

        def read(fd):
            """Function to read from a file descriptor."""
            return os.read(fd, 1024 * 1024).decode()

        # Create a pseudo-terminal
        master_fd, slave_fd = pty.openpty()

        # Spawn a new shell process
        shell = self.shell or detect_shell()[0]
        process = subprocess.Popen(
            [shell, self.interactive_opt],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            text=True,
        )
        self.set_environment(master_fd)

        # Wait for the shell to start and get to the prompt
        print(read(master_fd))

        # Send a command with a tab character for completion
        os.write(master_fd, (" ".join(cmds)).encode())
        time.sleep(0.5)
        os.write(master_fd, b"\t\t")

        # Read the output
        output = read_all_from_fd_with_timeout(master_fd, 3)

        # Clean up
        os.close(slave_fd)
        os.close(master_fd)
        process.terminate()
        process.wait()
        return output

    def run_app_completion(self):
        completions = self.get_completions(self.launch_script, "completion", " ")
        self.assertIn("django_typer", completions)
        self.assertIn("admin", completions)
        self.assertIn("auth", completions)
        self.assertIn("contenttypes", completions)
        self.assertIn("messages", completions)
        self.assertIn("sessions", completions)
        self.assertIn("staticfiles", completions)

    def test_shell_complete(self):
        with self.assertRaises(AssertionError):
            self.run_app_completion()
        self.install()
        self.run_app_completion()
        self.remove()
        with self.assertRaises(AssertionError):
            self.run_app_completion()
        self.install()


@pytest.mark.skipif(shutil.which("zsh") is None, reason="Z-Shell not available")
class ZshShellTests(DefaultCompleteTestCase):

    shell = "zsh"
    directory = Path("~/.zfunc").expanduser()

    def verify_install(self, script=DefaultCompleteTestCase.manage_script):
        if not script:
            script = self.command.manage_script_name
        self.assertTrue((self.directory / f"_{script}").exists())

    def verify_remove(self, script=DefaultCompleteTestCase.manage_script):
        if not script:
            script = self.command.manage_script_name
        self.assertFalse((self.directory / f"_{script}").exists())


@pytest.mark.skipif(shutil.which("bash") is None, reason="Bash not available")
class BashShellTests(DefaultCompleteTestCase):

    shell = "bash"
    directory = Path("~/.bash_completions").expanduser()

    def verify_install(self, script=DefaultCompleteTestCase.manage_script):
        if not script:
            script = self.command.manage_script_name
        self.assertTrue((self.directory / f"{script}.sh").exists())

    def verify_remove(self, script=DefaultCompleteTestCase.manage_script):
        if not script:
            script = self.command.manage_script_name
        self.assertFalse((self.directory / f"{script}.sh").exists())
