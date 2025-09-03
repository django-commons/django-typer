import re
import os
import pytest
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django_typer.config import traceback_config, use_rich_tracebacks
from django_typer.utils import with_typehint

from tests.utils import rich_installed, run_command
import platform


class TracebackConfigTests(with_typehint(TestCase)):
    rich_installed = True

    def test_default_traceback(self):
        result = run_command("test_command1", "--no-color", "delete", "me", "--throw")[
            1
        ]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)
        if self.rich_installed:
            self.assertIn("────────", result)
            # locals should not be present
            self.assertNotIn("name = 'me'", result)
            self.assertNotIn("throw = True", result)
            # by default we get only the last frame
            self.assertEqual(len(re.findall(r"\.py:\d+", result) or []), 1)

            hlp = run_command("test_command1", "--no-color", "--help")[0]
            # TODO - why are extra newlines inserted here on windows??
            if platform.system() == "Windows":
                hlp = hlp.replace("\r\n", "")
            self.assertNotIn("--hide-locals", hlp)
            self.assertIn("--show-locals", hlp)

            result = run_command(
                "test_command1",
                "--no-color",
                "--show-locals",
                "delete",
                "me",
                "--throw",
            )[1]
            self.assertIn("name = 'me'", result)
            self.assertIn("throw = True", result)
        else:
            self.assertNotIn("────────", result)

            hlp = run_command("test_command1", "--no-color", "--help")[0]
            self.assertNotIn("--hide-locals", hlp)
            self.assertNotIn("--show-locals", hlp)

    def test_tb_command_overrides(self):
        result = run_command(
            "test_tb_overrides", "--no-color", "delete", "me", "--throw"
        )[1]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)
        if self.rich_installed:
            self.assertIn("────────", result)
            # locals should be present
            self.assertIn("name = 'me'", result)
            self.assertIn("throw = True", result)
            # should get a stack trace with files and line numbers
            self.assertGreater(len(re.findall(r"\.py:\d+", result) or []), 0)

            hlp = run_command("test_tb_overrides", "--no-color", "--help")[0]

            # TODO - why are extra newlines inserted here on windows??
            if platform.system() == "Windows":
                hlp = hlp.replace("\r\n", "")
            self.assertIn("--hide-locals", hlp)
            self.assertNotIn("--show-locals", hlp)

            result = run_command(
                "test_tb_overrides",
                "--no-color",
                "--hide-locals",
                "delete",
                "me",
                "--throw",
            )[1]
            self.assertNotIn("name = 'me'", result)
            self.assertNotIn("throw = True", result)
        else:
            self.assertNotIn("────────", result)

            hlp = run_command("test_tb_overrides", "--no-color", "--help")[0]
            self.assertNotIn("--hide-locals", hlp)
            self.assertNotIn("--show-locals", hlp)

    def test_turn_traceback_off_false(self):
        result = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_tb_false",
            "delete",
            "me",
            "--throw",
        )[1]
        self.assertNotIn("────────", result)
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)

        hlp = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_tb_false",
            "--no-color",
            "--help",
        )[0]
        self.assertFalse("--show-locals" in hlp)
        self.assertFalse("--hide-locals" in hlp)

    @override_settings(DT_RICH_TRACEBACK_CONFIG=False)
    def test_traceback_set_to_false(self):
        self.assertEqual(traceback_config(), {"show_locals": False})
        self.assertIs(use_rich_tracebacks(), False)

    @override_settings(DT_RICH_TRACEBACK_CONFIG=True)
    def test_traceback_set_to_true(self):
        self.assertEqual(traceback_config(), {"show_locals": False})
        self.assertIs(use_rich_tracebacks(), self.rich_installed)

    @override_settings(DT_RICH_TRACEBACK_CONFIG=None)
    def test_traceback_set_to_none(self):
        self.assertEqual(traceback_config(), {"show_locals": False})
        self.assertIs(use_rich_tracebacks(), False)

    def test_turn_traceback_off_none(self):
        result = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_tb_none",
            "delete",
            "me",
            "--throw",
        )[1]
        self.assertNotIn("────────", result)
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)

        hlp = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_tb_none",
            "--no-color",
            "--help",
        )[0]
        self.assertFalse("--show-locals" in hlp)
        self.assertFalse("--hide-locals" in hlp)

    def test_traceback_no_locals_short_false(self):
        result = run_command(
            "test_command1",
            "--no-color",
            "--settings",
            "tests.settings.settings_tb_change_defaults",
            "delete",
            "me",
            "--throw",
        )[1]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)
        if self.rich_installed:
            self.assertIn("────────", result)
            self.assertGreater(len(re.findall(r"\.py:\d+", result) or []), 0)

            # locals should be present
            self.assertIn("name = 'me'", result)
            self.assertIn("throw = True", result)

            hlp = run_command(
                "test_command1",
                "--settings",
                "tests.settings.settings_tb_change_defaults",
                "--no-color",
                "--help",
            )[0]

            # TODO - why are extra newlines inserted here on windows??
            if platform.system() == "Windows":
                hlp = hlp.replace("\r\n", "")
            self.assertFalse("--show-locals" in hlp)
            self.assertTrue("--hide-locals" in hlp)
            result = run_command(
                "test_command1",
                "--no-color",
                "--hide-locals",
                "--settings",
                "tests.settings.settings_tb_change_defaults",
                "delete",
                "me",
                "--throw",
            )[1]

            self.assertNotIn("name = 'me'", result)
            self.assertNotIn("throw = True", result)
        else:
            self.assertNotIn("────────", result)

        self.assertNotIn("\x1b", result)

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="TODO --force-color not working on Windows",
    )
    def test_colored_traceback(self):
        result = run_command(
            "test_command1", "--force-color", "delete", "Brian", "--throw"
        )[1]
        if self.rich_installed:
            self.assertIn("\x1b", result)

        result = run_command(
            "test_command1", "--no-color", "delete", "Brian", "--throw"
        )[1]
        self.assertNotIn("\x1b", result)

        # the result of this depends on the terminal environment this runs in
        # result = run_command(
        #     "test_command1",
        #     "delete",
        #     "Brian",
        #     "--throw",
        # )[1]
        # self.assertIn("\x1b", result)


@pytest.mark.rich
@pytest.mark.skipif(not rich_installed, reason="rich not installed")
class TestTracebackConfig(TracebackConfigTests, TestCase):
    rich_installed = True

    @override_settings(DJ_RICH_TRACEBACK_CONFIG={"no_install": True})
    def test_tb_no_install(self):
        result = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_tb_no_install",
            "delete",
            "me",
        )[1]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: Test ready exception", result)
        self.assertNotIn("────────", result)
        self.assertNotIn("── locals ──", result)

        hlp = run_command(
            "test_command1", "--settings", "tests.settings.settings_tb_no_install"
        )[1]
        self.assertFalse("--show-locals" in hlp)
        self.assertFalse("--hide-locals" in hlp)

    def test_rich_install(self):
        result = run_command(
            "test_command1",
            "--settings",
            "tests.settings.settings_throw_init_exception",
            "--no-color",
            "delete",
            "me",
        )[1]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: Test ready exception", result)
        self.assertIn("────────", result)
        self.assertNotIn("── locals ──", result)
        self.assertNotIn("\x1b", result)


@pytest.mark.no_rich
@pytest.mark.skipif(rich_installed, reason="rich installed")
class TestTracebackConfigNoRich(TracebackConfigTests, TestCase):
    rich_installed = False


class TestSettingsSystemCheck(TestCase):
    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_warning_thrown(self):
        result = run_command(
            "noop", "--settings", "tests.settings.settings_tb_bad_config"
        )[1]
        if rich_installed:
            self.assertIn(
                "tests.settings.settings_tb_bad_config: (django_typer.W001) DT_RICH_TRACEBACK_CONFIG",
                result,
            )
            self.assertIn(
                "HINT: Unexpected parameters encountered: unexpected_setting.", result
            )
        else:
            self.assertNotIn(
                "tests.settings.settings_tb_bad_config: (django_typer.W001) DT_RICH_TRACEBACK_CONFIG",
                result,
            )


class TracebackTests(TestCase):
    """
    Tests that show CommandErrors and UsageErrors do not result in tracebacks unless --traceback is set.

    Also make sure that sys.exit is not called when not run from the terminal
    (i.e. in get_command invocation or call_command).
    """

    def test_usage_error_no_tb(self):
        stdout, stderr, retcode = run_command("tb", "--no-color", "wrong")
        self.assertTrue("manage.py tb [OPTIONS] COMMAND [ARGS]" in stdout)
        self.assertTrue("No such command" in stderr)
        self.assertTrue(retcode > 0)

        stdout, stderr, retcode = run_command("tb", "--no-color", "error", "wrong")
        self.assertTrue("manage.py tb error [OPTIONS]" in stdout)
        self.assertTrue("Got unexpected extra argument" in stderr)
        self.assertTrue(retcode > 0)

        with self.assertRaises(CommandError):
            call_command("tb", "wrong")

        with self.assertRaises(CommandError):
            call_command("tb", "error", "wrong")

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_usage_error_with_tb_if_requested(self):
        stdout, stderr, retcode = run_command(
            "tb", "--no-color", "--traceback", "wrong"
        )
        self.assertFalse(stdout.strip())
        self.assertTrue("Traceback" in stderr)
        if rich_installed:
            # self.assertTrue("───── locals ─────" in stderr)
            self.assertTrue("──────────── Traceback" in stderr)
        else:
            # self.assertFalse("───── locals ─────" in stderr)
            self.assertFalse("──────────── Traceback" in stderr)
        self.assertTrue("No such command 'wrong'" in stderr)
        self.assertTrue(retcode > 0)

        stdout, stderr, retcode = run_command(
            "tb", "--no-color", "--traceback", "error", "wrong"
        )
        self.assertFalse(stdout.strip())
        self.assertTrue("Traceback" in stderr)
        if rich_installed:
            # self.assertTrue("───── locals ─────" in stderr)
            self.assertTrue("──────────── Traceback" in stderr)
        else:
            # self.assertFalse("───── locals ─────" in stderr)
            self.assertFalse("──────────── Traceback" in stderr)
        self.assertFalse(stdout.strip())
        self.assertTrue("Got unexpected extra argument" in stderr)
        self.assertTrue(retcode > 0)

        with self.assertRaises(CommandError):
            call_command("tb", "--traceback", "wrong")

        with self.assertRaises(CommandError):
            call_command("tb", "--traceback", "error", "wrong")

    def test_click_exception_retcodes_honored(self):
        self.assertEqual(run_command("vanilla")[2], 0)
        self.assertEqual(run_command("vanilla", "--exit-code=2")[2], 2)

        self.assertEqual(run_command("tb", "exit")[2], 0)
        self.assertEqual(run_command("tb", "exit", "--code=2")[2], 2)

    def test_exit_on_call(self):
        with self.assertRaises(SystemExit):
            call_command("vanilla", "--help")

        with self.assertRaises(SystemExit):
            call_command("vanilla", "--exit-code", "0")

        with self.assertRaises(SystemExit):
            call_command("vanilla", "--exit-code", "1")

        with self.assertRaises(SystemExit):
            call_command("tb", "--help")

        with self.assertRaises(SystemExit):
            call_command("tb", "exit")

        with self.assertRaises(SystemExit):
            call_command("tb", "exit", "--code=1")
