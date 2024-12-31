import fcntl
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
import time
import typing as t
from pathlib import Path
import pytest
from functools import cached_property
import re
import subprocess

from shellingham import detect_shell

from django.test import TestCase
from django_typer.utils import with_typehint
from django_typer.management import get_command
from django_typer.management.commands.shellcompletion import Command as ShellCompletion
from ..utils import rich_installed

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


def scrub(output: str) -> str:
    """Scrub control code characters and ansi escape sequences for terminal colors from output"""
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", output, flags=re.IGNORECASE).replace(
        "\t", ""
    )


class _DefaultCompleteTestCase(with_typehint(TestCase)):
    shell = None
    manage_script = "manage.py"
    launch_script = "./manage.py"

    @property
    def interactive_opt(self):
        # currently all supported shells support -i for interactive mode
        # this includes zsh, bash, fish and powershell
        return "-i"

    @cached_property
    def command(self) -> ShellCompletion:
        return get_command("shellcompletion", ShellCompletion)

    def setUp(self):
        self.remove()
        super().setUp()

    def tearDown(self):
        self.remove()
        super().tearDown()

    def verify_install(self, script=None):
        pass

    def verify_remove(self, script=None):
        pass

    def install(self, script=None, force_color=False, no_color=None):
        if not script:
            script = self.manage_script
        init_kwargs = {"force_color": force_color, "no_color": no_color}
        kwargs = {}
        if script:
            kwargs["manage_script"] = script
        if self.shell:
            init_kwargs["shell"] = self.shell
        self.command.init(**init_kwargs)
        self.command.install(**kwargs)
        self.verify_install(script=script)

    def remove(self, script=None):
        if not script:
            script = self.manage_script
        kwargs = {}
        if script:
            kwargs["manage_script"] = script
        if self.shell:
            self.command.init(shell=self.shell)
        self.command.uninstall(**kwargs)
        self.get_completions("ping")  # just to reinit shell
        self.verify_remove(script=script)

    def set_environment(self, fd):
        os.write(fd, f"PATH={Path(sys.executable).parent}:$PATH\n".encode())
        os.write(
            fd,
            f"DJANGO_SETTINGS_MODULE=tests.settings.completion\n".encode(),
        )

    def get_completions(self, *cmds: str, scrub_output=True) -> str:
        def read(fd):
            """Function to read from a file descriptor."""
            return os.read(fd, 1024 * 1024).decode()

        # Create a pseudo-terminal
        master_fd, slave_fd = pty.openpty()

        # Define window size - width and height
        os.set_blocking(slave_fd, False)
        win_size = struct.pack("HHHH", 24, 80, 0, 0)  # 24 rows, 80 columns
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, win_size)

        # env = os.environ.copy()
        # env["TERM"] = "xterm-256color"

        # Spawn a new shell process
        shell = self.shell or detect_shell()[0]
        process = subprocess.Popen(
            [shell, *([self.interactive_opt] if self.interactive_opt else [])],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            text=True,
            # env=env,
            # preexec_fn=os.setsid,
        )
        # Wait for the shell to start and get to the prompt
        print(read(master_fd))

        self.set_environment(master_fd)

        print(read(master_fd))
        # Send a command with a tab character for completion

        cmd = " ".join(cmds)
        os.write(master_fd, cmd.encode())
        time.sleep(0.5)

        print(f'"{cmd}"')
        os.write(master_fd, b"\t\t")

        time.sleep(0.5)

        # Read the output
        output = read_all_from_fd_with_timeout(master_fd, 3)

        # todo - avoid large output because this can mess things up
        if "do you wish" in output or "Display all" in output:
            os.write(master_fd, b"y\n")
            time.sleep(0.5)
            output = read_all_from_fd_with_timeout(master_fd, 3)

        # Clean up
        os.close(slave_fd)
        os.close(master_fd)
        process.terminate()
        process.wait()
        # remove bell character which can show up in some terminals where we hit tab
        if scrub_output:
            return scrub(output)
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

    def run_bad_command_completion(self):
        completions = self.get_completions(
            self.launch_script, "completion_does_not_exist", " "
        )
        self.assertTrue("Exception" not in completions)
        self.assertTrue("traceback" not in completions)

    def run_command_completion(self):
        completions = self.get_completions(self.launch_script, "complet")
        self.assertIn("completion", completions)
        completions = self.get_completions(self.launch_script)
        self.assertIn("changepassword", completions)
        self.assertIn("check", completions)
        self.assertIn("dumpdata", completions)
        self.assertIn("completion", completions)
        self.assertIn("collectstatic", completions)

    def run_rich_option_completion(self, rich_output_expected: bool):
        completions = self.get_completions(
            self.launch_script, "completion", "--cmd", scrub_output=False
        )
        self.assertIn("--cmd", completions)
        self.assertIn("--cmd-first", completions)
        self.assertIn("--cmd-dup", completions)
        if not rich_installed:
            self.assertIn("[bold]", completions)
            self.assertIn("[/bold]", completions)
            self.assertIn("[reverse]", completions)
            self.assertIn("[/reverse]", completions)
            self.assertIn("[underline]", completions)
            self.assertIn("[/underline]", completions)
            self.assertIn("[yellow]", completions)
            self.assertIn("[/yellow]", completions)
        elif rich_output_expected:
            self.assertIn("\x1b[7mcommands\x1b[0m", completions)
            self.assertIn("\x1b[4;33mcommands\x1b[0m", completions)
            self.assertIn("\x1b[1mimport path\x1b[0m", completions)
            self.assertIn("\x1b[1mname\x1b[0m", completions)
        else:
            self.assertNotIn("\x1b[7mcommands\x1b[0m", completions)
            self.assertNotIn("\x1b[4;33mcommands\x1b[0m", completions)
            self.assertNotIn("\x1b[1mimport path\x1b[0m", completions)
            self.assertNotIn("\x1b[1mname\x1b[0m", completions)

    def test_shell_complete(self):
        with self.assertRaises(AssertionError):
            self.run_app_completion()
        self.install()
        self.run_app_completion()
        self.run_bad_command_completion()
        self.run_command_completion()
        self.remove()
        with self.assertRaises(AssertionError):
            self.run_app_completion()
        self.install()

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_rich_output(self):
        self.install(force_color=True)
        self.run_rich_option_completion(rich_output_expected=True)

    @pytest.mark.rich
    @pytest.mark.skipif(not rich_installed, reason="Rich not installed")
    def test_no_rich_output(self):
        self.install(no_color=True)
        self.run_rich_option_completion(rich_output_expected=False)

    def test_settings_pass_through(self):
        # https://github.com/django-commons/django-typer/issues/68
        self.install()
        completions = self.get_completions(self.launch_script, "app_labels", " ")
        self.assertNotIn("django_typer", completions)
        completions = self.get_completions(
            self.launch_script,
            "app_labels",
            "--settings",
            "tests.settings.examples",
            " ",
        )
        self.assertIn("django_typer", completions)

    def test_pythonpath_pass_through(self):
        # https://github.com/django-commons/django-typer/issues/68
        self.install()
        completions = self.get_completions(
            self.launch_script, "python_path", "--options", " "
        )
        self.assertNotIn("working", completions)
        completions = self.get_completions(
            self.launch_script,
            "python_path",
            "--pythonpath",
            "tests/off_path",
            "--option",
            " ",
        )
        self.assertIn("working", completions)


class _InstalledScriptTestCase(_DefaultCompleteTestCase):
    """
    These shell completes use an installed script available on the path
    instead of a script directly invoked by path. The difference may
    seem trivial - but it is not given how most shells determine if completion
    logic should be invoked for a given command.
    """

    MANAGE_SCRIPT_TMPL = Path(__file__).parent / "django_manage.py"
    manage_script = "django_manage"
    launch_script = "django_manage"

    def setUp(self):
        lines = []
        with open(self.MANAGE_SCRIPT_TMPL, "r") as f:
            for line in f.readlines():
                if line.startswith("#!{{shebang}}"):
                    line = f"#!{sys.executable}\n"
                lines.append(line)
        exe = Path(sys.executable).parent / self.manage_script
        with open(exe, "w") as f:
            for line in lines:
                f.write(line)

        # make the script executable
        os.chmod(exe, os.stat(exe).st_mode | 0o111)
        super().setUp()
