import codecs
import os
import re
import select
import struct
import subprocess
import sys
import time
import typing as t
from pathlib import Path
import pytest
from functools import cached_property
import platform
from django.test import TestCase

from django_typer.utils import detect_shell

from django_typer.management import get_command
from django_typer.management.commands.shellcompletion import Command as ShellCompletion
from django_typer.shells import DjangoTyperShellCompleter
from django_typer.utils import with_typehint
from ..utils import rich_installed, manage_py

default_shell = None

try:
    default_shell = detect_shell()[0]
except Exception:
    pass


def flat_scrub(output: str) -> str:
    """Strip ALL ANSI/escape sequences without simulating a terminal screen.

    Use this instead of :func:`render` for shells whose completion display
    is *ephemeral* -- i.e. characters drawn to the screen and then erased
    by a follow-up control sequence (cursor-up + ``\\x1b[J`` erase-below
    is the canonical pattern). Pyte faithfully replays such erasures and
    loses the text, but for an assertion like ``assertIn("completers")``
    we want to know what was *transmitted*, not what survived on a final
    rendered screen.

    Currently used by fish (the pager that displays multi-candidate
    completion menus closes itself when extra input arrives and
    overwrites its own region of the screen).
    """
    # CSI sequences (covers SGR colors, cursor moves, mode toggles,
    # private/extended forms like \x1b[?2004h, \x1b[>4;1m, \x1b[=5u).
    output = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", output)
    # OSC sequences (set window title etc.): ESC ] ... BEL | ST.
    output = re.sub(r"\x1B\][^\x07\x1B]*(?:\x07|\x1B\\)", "", output)
    # Character set designation: ESC ( B, ESC ) 0, ESC * B, ESC + B.
    output = re.sub(r"\x1B[\(\)*+][\dA-Z=]", "", output)
    # Two-char escape forms: ESC =, ESC >, ESC 7, ESC 8.
    output = re.sub(r"\x1B[=>78]", "", output)
    # Stray control chars that aren't escape-introduced.
    return output.replace("\x08", "").replace("\t", "").replace("\r", "")


def render(output: str, cols: int = 500, rows: int = 200) -> str:
    """Render terminal control sequences via pyte to recover visible screen text.

    Why: bash's readline redisplay emits cursor-positioning codes interleaved
    with literal characters and pad-spaces. Stripping CSI sequences leaves the
    chars at the *wrong* positions (e.g. ``complet                  ion``),
    so substring assertions against the resulting string fail even though the
    user would see ``completion`` on their terminal. pyte replays the codes
    against a virtual screen and gives us back what's actually visible.

    The virtual screen is intentionally far wider than the PTY (which is 80
    cols). Shells often wrap long input/output implicitly when the cursor
    runs past the PTY's last column -- the byte stream contains no newline,
    so a virtual screen matching the PTY would split the text. A wider
    screen lets pyte keep the text on one row, matching the contiguous
    substring we want to assert against (e.g. a long filesystem path).
    """
    import pyte

    screen = pyte.Screen(cols, rows)
    stream = pyte.Stream(screen)
    stream.feed(output)
    return "\n".join(line.rstrip() for line in screen.display).rstrip()


_SENTINEL_PREFIX = "__DJT_SENTINEL_"

# Sentinel byte written immediately after TAB. Because shell input is
# processed serially, this character can only be echoed back AFTER the
# shell has finished the TAB-triggered completion (subprocess call +
# line rewrite). Spotting it in the captured stream is a positive
# "completion is done" signal that avoids relying on a long
# silence-based quiet_period.
#
# Chosen as a multi-byte UTF-8 character that is exceedingly unlikely
# to appear in any real completion candidate, in shell prompts, or in
# terminal escape sequences (so it won't false-match in the captured
# stream). Trade-off: PSReadLine reads input byte-by-byte and treats
# the individual high-bit bytes (0xe2, 0x80, 0xa1 for ``‡``) as
# Meta-key prefixes that flip the line into continuation-prompt state,
# so PowerShell opts out of the sentinel path -- see ``tab_sentinel``.
#
# Single-byte ASCII alternatives (``~``, ``Q``, etc.) were tried but
# either appear in shell prompts / escape sequences (false-match) or
# in completion output (collision with .replace strip).
_TAB_SENTINEL = "‡"


def _wait_for(
    read_fn: t.Callable[[], str],
    sentinel: t.Optional[str] = None,
    quiet_period: float = 0.25,
    timeout: float = 15.0,
) -> str:
    """
    Poll ``read_fn`` until either:
      * ``sentinel`` (if provided) has appeared and no new bytes arrived
        for ``quiet_period`` seconds, OR
      * no sentinel was given and no new bytes arrived for ``quiet_period``
        seconds (pure quiescence wait).

    Always bounded by ``timeout``. Returns the full buffer.
    """
    buf = ""
    start = time.time()
    last_data = time.time()
    seen = sentinel is None
    while time.time() - start < timeout:
        data = read_fn()
        if data:
            buf += data
            last_data = time.time()
            if sentinel is not None and not seen and sentinel in buf:
                seen = True
        elif seen and (time.time() - last_data) >= quiet_period:
            return buf
        else:
            time.sleep(0.02)
    return buf


class _CompleteTestCase(with_typehint(TestCase)):
    shell: str
    manage_script: str
    launch_script: str

    interactive_opt: t.Optional[str] = None

    environment: t.List[str] = []

    tabs: str

    # When True (Unix only), spawn the shell with os.setsid() + TIOCSCTTY so
    # the child becomes session leader with a proper controlling terminal.
    # Fish requires this -- it disables interactive features (including TAB
    # completion) without a controlling TTY. zsh on the other hand REGRESSES
    # under this setup -- ZLE / job-control init paths differ enough that
    # our captured-output flow stops working. Bash is unaffected either way.
    requires_controlling_terminal: bool = False

    # When non-None, write this string immediately after TAB and wait for it
    # to be echoed back as a positive "completion is done" signal. Shells
    # process input serially, so the sentinel is guaranteed to be processed
    # only AFTER the TAB-triggered completion finishes. Set to None to fall
    # back to a pure quiet-period wait -- required for PowerShell, where
    # PSReadLine interprets the multi-byte UTF-8 sentinel bytes (0xe2 0x80
    # 0xa1 for ``‡``) as Meta-key chord input that puts the line into
    # continuation-prompt state, breaking completion entirely.
    tab_sentinel: t.Optional[str] = _TAB_SENTINEL

    # Quiet period (seconds of silence) used when ``tab_sentinel`` is None.
    # Must be long enough to bridge the Django-bootstrap gap between echoing
    # the typed text and the completion subprocess actually producing
    # output. On slow CI VMs (especially Windows) cold-start Django can
    # take 3-4s, so we default to a generous value.
    tab_quiet_period: float = 4.0

    # Per-instance shell process state (None when no shell is running).
    _shell_state: t.Any = None
    _sentinel_counter: int = 0
    # Incremental UTF-8 decoder (Unix path), recreated per shell spawn. A
    # multi-byte UTF-8 sequence -- notably the 3-byte tab sentinel -- can
    # straddle two os.read() chunks; a plain per-chunk decode would mangle
    # it into replacement characters and the sentinel would never match.
    _decoder: t.Any = None

    @cached_property
    def command(self) -> ShellCompletion:
        cmd = get_command("shellcompletion", ShellCompletion)
        cmd.init(shell=self.shell)
        return cmd

    def get_completer(self, **kwargs) -> DjangoTyperShellCompleter:
        return self.command.shell_class(
            **{"prog_name": self.manage_script, "command": self.command, **kwargs}
        )

    def setUp(self):
        self._shell_state = None
        self._sentinel_counter = 0
        self.remove()
        super().setUp()

    def tearDown(self):
        self.remove()
        self._invalidate_shell()
        super().tearDown()

    def _next_sentinel(self) -> str:
        self._sentinel_counter += 1
        return f"{_SENTINEL_PREFIX}{self._sentinel_counter}__"

    def _invalidate_shell(self) -> None:
        """Tear down the current shell process, if any.

        Called whenever shell state (profile, registered completers) may
        have changed and a fresh shell process is required.
        """
        state = self._shell_state
        self._shell_state = None
        if state is None:
            return
        if platform.system() == "Windows":
            # winpty.PTY exposes no close()/terminate() API. Dropping the
            # last reference frees the underlying console, which terminates
            # the attached shell process.
            del state
        else:
            master_fd, slave_fd, process = state
            # Close the fds first so the shell sees EOF on stdin and exits
            # cleanly.  This avoids relying on SIGTERM, which some shells
            # (notably interactive zsh) ignore.
            for fd in (master_fd, slave_fd):
                try:
                    os.close(fd)
                except Exception:
                    pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.wait(timeout=2)
                except Exception:
                    pass

    def verify_install(self, script=None, directory: t.Optional[Path] = None):
        pass

    def verify_remove(self, script=None, directory: t.Optional[Path] = None):
        pass

    def install(
        self,
        script=None,
        force_color=False,
        no_color=None,
        fallback=None,
        no_shell=False,
        prompt=False,
    ):
        if not script:
            script = self.manage_script
        init_kwargs = {"force_color": force_color, "no_color": no_color}
        kwargs = {"prompt": prompt}
        if script:
            kwargs["manage_script"] = script
        if self.shell and not no_shell:
            init_kwargs["shell"] = self.shell
        if fallback:
            kwargs["fallback"] = fallback
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
        self.verify_remove(script=script)

    # ------------------------------------------------------------------ #
    # PTY plumbing
    #
    # Each get_completions() spawns a fresh shell, sources the environment,
    # types the command + TAB, captures output, and tears the shell down.
    # The previous implementation also spawned per-call but relied on fixed
    # time.sleep() calls (3s for the first prompt + 2s after env + 2s after
    # TAB).  Here those are replaced with sentinel-based waits (after each
    # silent command we echo a unique marker and read until it appears) and
    # pure quiescence waits after TAB (where no sentinel is possible).
    # ------------------------------------------------------------------ #

    if platform.system() == "Windows":

        def _read_shell(self) -> str:
            return self._shell_state.read() if self._shell_state is not None else ""

        def _write_shell(self, data: str) -> None:
            assert self._shell_state is not None
            self._shell_state.write(data)

        def _ensure_shell(self) -> None:
            if self._shell_state is not None:
                return
            import winpty

            assert self.shell

            self._shell_state = winpty.PTY(256, 512)
            self._shell_state.spawn(
                self.shell, *([self.interactive_opt] if self.interactive_opt else [])
            )

            # Wait for first prompt by echoing a sentinel; the shell will
            # process it once the prompt is ready.
            sentinel = self._next_sentinel()
            self._write_shell(f"echo {sentinel}{os.linesep}")
            _wait_for(self._read_shell, sentinel=sentinel, timeout=20.0)

            for line in self.environment:
                self._write_shell(f"{line}{os.linesep}")
                sentinel = self._next_sentinel()
                self._write_shell(f"echo {sentinel}{os.linesep}")
                _wait_for(self._read_shell, sentinel=sentinel, timeout=15.0)

    else:

        def _read_shell(self) -> str:
            if self._shell_state is None:
                return ""
            master_fd = self._shell_state[0]
            rlist, _, _ = select.select([master_fd], [], [], 0)
            if not rlist:
                return ""
            try:
                data = os.read(master_fd, 1024 * 1024)
            except (BlockingIOError, OSError):
                return ""
            if not data:
                return ""
            return self._decoder.decode(data)

        def _write_shell(self, data: str) -> None:
            assert self._shell_state is not None
            os.write(self._shell_state[0], data.encode())

        def _ensure_shell(self) -> None:
            if self._shell_state is not None:
                return
            import fcntl
            import termios
            import pty

            self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            master_fd, slave_fd = pty.openpty()
            os.set_blocking(slave_fd, False)
            os.set_blocking(master_fd, False)
            win_size = struct.pack("HHHH", 24, 80, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, win_size)

            def _become_session_leader() -> None:
                # Give the child a proper controlling terminal. Fish refuses
                # to run interactively without one (prints "warning: No TTY
                # for interactive shell" and disables completion / readline).
                os.setsid()
                fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)

            shell = self.shell or detect_shell()[0]
            process = subprocess.Popen(
                [shell, *([self.interactive_opt] if self.interactive_opt else [])],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                text=True,
                preexec_fn=(
                    _become_session_leader
                    if self.requires_controlling_terminal
                    else None
                ),
            )
            self._shell_state = (master_fd, slave_fd, process)

            sentinel = self._next_sentinel()
            self._write_shell(f"echo {sentinel}{os.linesep}")
            _wait_for(self._read_shell, sentinel=sentinel, timeout=15.0)

            for line in self.environment:
                self._write_shell(f"{line}{os.linesep}")
                sentinel = self._next_sentinel()
                self._write_shell(f"echo {sentinel}{os.linesep}")
                _wait_for(self._read_shell, sentinel=sentinel, timeout=10.0)

    def get_completions(self, *cmds: str, scrub_output=True, position=0) -> str:
        # Ensure a clean shell for every call; previous test interactions
        # (typed but un-Entered text, completion menus, prediction overlays)
        # could otherwise contaminate the captured output.
        self._invalidate_shell()
        self._ensure_shell()
        try:
            self._write_shell(" ".join(cmds))
            if position > 0:
                self._write_shell("\x1b[C" * position)
            elif position < 0:
                self._write_shell("\x1b[D" * abs(position))
            self._write_shell(self.tabs)
            if self.tab_sentinel is not None:
                # Sentinel-after-TAB: shells process input serially, so
                # this character can only be echoed back AFTER TAB-
                # triggered completion has fully finished (including the
                # Django subprocess call that powers our completer).
                # Waiting for the sentinel in the captured stream is
                # much faster and more reliable than waiting for a quiet
                # period long enough to cover slow CI Django boots.
                self._write_shell(self.tab_sentinel)
                output = _wait_for(
                    self._read_shell,
                    sentinel=self.tab_sentinel,
                    quiet_period=0.3,
                    timeout=25.0,
                )
            else:
                # Sentinel-less path: fall back to pure quiet-period
                # detection. Required for PowerShell -- see comment on
                # ``tab_sentinel``.
                output = _wait_for(
                    self._read_shell,
                    quiet_period=self.tab_quiet_period,
                    timeout=25.0,
                )
        finally:
            self._invalidate_shell()

        # Strip the sentinel (no-op for sentinel-less shells) so callers
        # never see this test artifact in the rendered completion output.
        if self.tab_sentinel is not None:
            output = output.replace(self.tab_sentinel, "")
        return self._render_output(output) if scrub_output else output

    def _render_output(self, output: str) -> str:
        """Convert raw PTY bytes to assertion-friendly text.

        Default implementation uses :func:`render` (pyte-based) which
        accurately reflects the *final* visible screen state. Shells whose
        completion menus are drawn-then-overwritten (notably fish)
        override this to use :func:`flat_scrub` so candidate text that
        was transmitted but later erased remains in the result.
        """
        return render(output)

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
        completions = self.get_completions(self.launch_script, " ")
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
            if self.shell not in ["powershell", "pwsh"]:
                self.assertIn("[bold]", completions)
                self.assertIn("[/bold]", completions)
                self.assertIn("[reverse]", completions)
                self.assertIn("[/reverse]", completions)
                self.assertIn("[underline]", completions)
                self.assertIn("[/underline]", completions)
                self.assertIn("[yellow]", completions)
                self.assertIn("[/yellow]", completions)
            else:
                self.assertTrue(
                    "[bold]" in completions
                    or "[/bold]" in completions
                    or "[reverse]" in completions
                    or "[/reverse]" in completions
                    or "[underline]" in completions
                    or "[/underline]" in completions
                    or "[yellow]" in completions
                    or "[/yellow]" in completions
                )
        elif rich_output_expected:
            # \x1b[0m and \x1b[m are the same
            if self.shell not in ["powershell", "pwsh"]:
                # exempt powershell from this because it filters the codes anyway
                self.assertIn("\x1b[7mcommands\x1b[", completions)
                self.assertIn("\x1b[4;33mcommands\x1b[", completions)
                self.assertIn("\x1b[1mname\x1b[", completions)
        else:
            self.assertNotIn("\x1b[7mcommands\x1b[", completions)
            self.assertNotIn("\x1b[4;33mcommands\x1b[", completions)
            self.assertNotIn("\x1b[1mimport path\x1b[", completions)
            self.assertNotIn("\x1b[1mname\x1b[", completions)

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

    def test_fallback(self):
        self.remove()
        self.install(fallback="tests.fallback.custom_fallback")
        completions = self.get_completions(self.launch_script, " ")
        self.assertIn("custom_fallback", completions)

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
        completions = self.get_completions(
            self.launch_script,
            "app_labels",
            "--settings=tests.settings.examples",
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
        completions = self.get_completions(
            self.launch_script,
            "python_path",
            "--pythonpath=tests/off_path",
            "--option",
            " ",
        )
        self.assertIn("working", completions)

    def test_reentrant_install_uninstall(self):
        self.install()
        self.install()
        self.verify_install()

        completions = self.get_completions(self.launch_script, "complet")
        self.assertIn("completion", completions)

        self.remove()
        self.remove()
        self.verify_remove()

    def test_path_completion(self):
        self.install()
        self.verify_install()
        completions = self.get_completions(
            self.launch_script, "completion", "--path", "./src/django_typer/co"
        )
        self.assertIn("completers", completions)
        self.assertIn("config.py", completions)
        completions = self.get_completions(
            self.launch_script, "completion", "--dir", "./src/django_typer/"
        )
        self.assertNotIn("utils.py", completions)
        self.assertNotIn("config.py", completions)
        self.assertIn("templates", completions)
        self.assertIn("management", completions)
        self.remove()
        self.verify_remove()

    # todo - cursor positioning not working
    # def test_cursor_position(self):
    #     self.install()
    #     self.verify_install()
    #     cmd = [self.launch_script, "shellcompletion", "--set ", "install"]
    #     completions = self.get_completions(*cmd, position=-9)
    #     self.assertIn("--settings", completions)
    #     self.remove()
    #     self.verify_remove()


class _ScriptCompleteTestCase(_CompleteTestCase):
    manage_script: str = "manage.py"
    launch_script: str = "./manage.py"


class _InstalledScriptCompleteTestCase(_CompleteTestCase):
    """
    These shell completes use an installed script available on the path
    instead of a script directly invoked by path. The difference may
    seem trivial - but it is not given how most shells determine if completion
    logic should be invoked for a given command.
    """

    MANAGE_SCRIPT_TMPL = Path(__file__).parent / "django_manage.py"
    manage_script = "django-admin"
    launch_script = "django-admin"

    @classmethod
    def install_script(cls, script=None):
        if not script:
            script = cls.manage_script
        lines = []
        with open(cls.MANAGE_SCRIPT_TMPL, "r") as f:
            for line in f.readlines():
                if line.startswith("#!{{shebang}}"):
                    line = f"#!{sys.executable}\n"
                lines.append(line)
        exe = Path(sys.executable).parent / script
        with open(exe, "w") as f:
            for line in lines:
                f.write(line)

        # make the script executable
        os.chmod(exe, os.stat(exe).st_mode | 0o111)

        if platform.system() == "Windows":
            with open(exe.with_suffix(".cmd"), "w") as f:
                f.write(f'@echo off{os.linesep}"{sys.executable}" "%~dp0{exe.name}" %*')
            os.chmod(exe, os.stat(exe.with_suffix(".cmd")).st_mode | 0o111)

    @classmethod
    def remove_script(cls, script=None):
        if not script:
            script = cls.manage_script
        exe = Path(sys.executable).parent / script
        exe.unlink(missing_ok=True)
        exe.with_suffix(".cmd").unlink(missing_ok=True)

    def test_multi_install(self):
        parts = self.manage_script.split(".")
        manage2 = ".".join([parts[0] + "2", *parts[1:]])
        try:
            self.install_script(script=manage2)
            self.install()
            self.verify_install()
            self.install(script=manage2)
            self.verify_install(script=manage2)

            completions = self.get_completions(self.manage_script, "complet")
            self.assertIn("completion", completions)

            completions = self.get_completions(manage2, "complet")
            self.assertIn("completion", completions)

            self.remove()
            self.verify_remove()
            self.remove(script=manage2)
            self.verify_remove(script=manage2)
        finally:
            self.remove_script(script=manage2)

    def test_prompt_install(self, env={}, directory: t.Optional[Path] = None):
        import pexpect

        env = {
            **dict(os.environ),
            "DJANGO_SETTINGS_MODULE": "tests.settings.completion",
            "DJANGO_COLORS": "nocolor",
            **env,
        }

        rex = re.compile
        expected = [
            rex(
                r"Append\s+the\s+above\s+contents\s+to\s+(?P<file>.*)\?", re.DOTALL
            ),  # 0
            rex(
                r"Create\s+(?P<file>.*)\s+with\s+the\s+above\s+contents\?",
                re.DOTALL,
            ),  # 1
            rex(r"Aborted\s+shell\s+completion\s+installation."),  # 2
            rex(rf"Installed\s+autocompletion\s+for\s+{self.shell}"),  # 3
        ]

        install_command = [
            "shellcompletion",
            "--no-color",
            "--shell",
            self.shell,
            "install",
        ]
        self.remove()
        self.verify_remove(directory=directory)

        if platform.system() != "Windows":
            install = pexpect.spawn(self.manage_script, install_command, env=env)
            install.setwinsize(24, 800)
        else:
            from pexpect.popen_spawn import PopenSpawn

            install = PopenSpawn(
                " ".join([self.manage_script, *install_command]),
                env=env,
                encoding="utf-8",
            )

        def wait_for_output(child) -> t.Tuple[int, t.Optional[str]]:
            index = child.expect(expected)
            if index in [0, 1]:
                return index, child.match.group("file")
            return index, None

        # test an abort
        idx, _ = wait_for_output(install)
        self.assertLess(idx, 2)
        install.sendline("N")

        while True:
            idx, _ = wait_for_output(install)
            if idx < 2:
                install.sendline("N")
            else:
                self.assertEqual(idx, 2)
                break

        self.verify_remove(directory=directory)

        # test an install
        if platform.system() != "Windows":
            install = pexpect.spawn(self.manage_script, install_command, env=env)
            install.setwinsize(24, 800)
        else:
            from pexpect.popen_spawn import PopenSpawn

            install = PopenSpawn(
                " ".join([self.manage_script, *install_command]),
                env=env,
                encoding="utf-8",
            )

        while True:
            idx, _ = wait_for_output(install)
            if idx < 2:
                install.sendline("Y")
            else:
                self.assertEqual(idx, 3)
                break

        self.verify_install(directory=directory)

    # TODO
    # else:

    #     def test_prompt_install(self, env={}, directory: t.Optional[Path] = None):
    #         env = {
    #             **dict(os.environ),
    #             "DJANGO_SETTINGS_MODULE": "tests.settings.completion",
    #             "DJANGO_COLORS": "nocolor",
    #             **env,
    #         }

    #         rex = re.compile
    #         expected_patterns = [
    #             rex(r"Append the above contents to (?P<file>.*)\?"),  # 0
    #             rex(r"Create (?P<file>.*) with the above contents\?"),  # 1
    #             rex(r"Aborted shell completion installation."),  # 2
    #             rex(rf"Installed autocompletion for {self.shell}"),  # 3
    #         ]

    #         install_command = [
    #             self.manage_script,
    #             "shellcompletion",
    #             "--no-color",
    #             "--shell",
    #             self.shell,
    #             "install",
    #         ]
    #         self.remove()
    #         self.verify_remove(directory=directory)

    #         def run_with_response(responses: t.List[str]):
    #             process = subprocess.Popen(
    #                 install_command,
    #                 env=env,
    #                 cwd=directory,
    #                 stdin=subprocess.PIPE,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.STDOUT,
    #                 text=True,
    #             )

    #             output = ""
    #             for response in responses:
    #                 while True:
    #                     line = process.stdout.readline()
    #                     if not line:
    #                         break
    #                     output += line

    #                     matched_index, matched_file = match_output(line)
    #                     if matched_index is not None:
    #                         process.stdin.write(response + "\n")
    #                         process.stdin.flush()
    #                         break

    #             process.wait()
    #             return output

    #         def match_output(line: str) -> t.Tuple[t.Optional[int], t.Optional[str]]:
    #             for i, pattern in enumerate(expected_patterns):
    #                 match = pattern.search(line)
    #                 if match:
    #                     return i, match.groupdict().get("file")
    #             return None, None

    #         # Test abort sequence
    #         abort_output = run_with_response(["N", "N"])
    #         self.assertIn("Aborted shell completion installation.", abort_output)
    #         self.verify_remove(directory=directory)

    #         # Test install sequence
    #         install_output = run_with_response(["Y", "Y"])
    #         self.assertIn(f"Installed autocompletion for {self.shell}", install_output)
    #         self.verify_install(directory=directory)
