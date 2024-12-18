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

from shellingham import detect_shell

from django_typer.management import get_command
from django_typer.management.commands.shellcompletion import Command as ShellCompletion

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
    return re.sub(r"[\x00-\x1F\x7F]|\x1B\[[0-?]*[ -/]*[@-~]", "", output).replace(
        "\t", ""
    )


class _DefaultCompleteTestCase:
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

    def install(self, script=None):
        if not script:
            script = self.manage_script
        kwargs = {}
        if script:
            kwargs["manage_script"] = script
        if self.shell:
            self.command.init(shell=self.shell)
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
        self.verify_remove(script=script)

    def set_environment(self, fd):
        os.write(fd, f"PATH={Path(sys.executable).parent}:$PATH\n".encode())
        os.write(
            fd,
            f'DJANGO_SETTINGS_MODULE={os.environ["DJANGO_SETTINGS_MODULE"]}\n'.encode(),
        )

    def get_completions(self, *cmds: str) -> t.List[str]:
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

        os.write(master_fd, (" ".join(cmds)).encode())
        time.sleep(0.5)

        print(f'"{(" ".join(cmds))}"')
        os.write(master_fd, b"\t\t")

        time.sleep(0.5)

        # Read the output
        output = read_all_from_fd_with_timeout(master_fd, 3)

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
        return scrub(output)

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
        # annoingly in CI there are some spaces inserted between the incomplete phrase
        # and the completion on linux in bash specifically
        self.assertTrue(re.match(r".*complet\s*ion.*", completions))
        completions = self.get_completions(self.launch_script, " ")
        self.assertIn("adapted", completions)
        self.assertIn("help_precedence", completions)
        self.assertIn("closepoll", completions)

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
