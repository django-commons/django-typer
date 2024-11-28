import re

import pytest
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from tests.utils import rich_installed, run_command
import platform


@pytest.mark.skipif(not rich_installed, reason="rich not installed")
class TestTracebackConfig(TestCase):
    rich_installed = True

    uninstall = False

    def test_default_traceback(self):
        result = run_command("test_command1", "--no-color", "delete", "me", "--throw")[
            1
        ]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)
        if rich_installed:
            self.assertIn("────────", result)
            # locals should be present
            self.assertIn("name = 'me'", result)
            self.assertIn("throw = True", result)
            # by default we get only the last frame
            self.assertEqual(len(re.findall(r"\.py:\d+", result) or []), 1)
        else:
            self.assertNotIn("────────", result)

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_tb_command_overrides(self):
        result = run_command(
            "test_tb_overrides", "--no-color", "delete", "me", "--throw"
        )[1]
        self.assertIn("Traceback (most recent call last)", result)
        self.assertIn("Exception: This is a test exception", result)
        if rich_installed:
            self.assertIn("────────", result)
            # locals should be present
            self.assertNotIn("name = 'me'", result)
            self.assertNotIn("throw = True", result)
            # should get a stack trace with files and line numbers
            self.assertGreater(len(re.findall(r"\.py:\d+", result) or []), 0)
        else:
            self.assertNotIn("────────", result)

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

    @pytest.mark.rich
    @pytest.mark.no_rich
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
        # locals should not be present
        self.assertNotIn("name = 'me'", result)
        self.assertNotIn("throw = True", result)
        if rich_installed:
            self.assertIn("────────", result)
            self.assertGreater(len(re.findall(r"\.py:\d+", result) or []), 0)
        else:
            self.assertNotIn("────────", result)

        self.assertNotIn("\x1b", result)

    @pytest.mark.rich
    @pytest.mark.skipif(not rich_installed, reason="rich not installed")
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
        self.assertIn("── locals ──", result)
        self.assertNotIn("\x1b", result)

    @pytest.mark.rich
    @pytest.mark.skipif(not rich_installed, reason="rich is not installed")
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

    @pytest.mark.rich
    @pytest.mark.no_rich
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="TODO --force-color not working on Windows",
    )
    def test_colored_traceback(self):
        result = run_command(
            "test_command1", "--force-color", "delete", "Brian", "--throw"
        )[1]
        if rich_installed:
            self.assertIn("\x1b", result)

        result = run_command(
            "test_command1", "--no-color", "delete", "Brian", "--throw"
        )[1]
        self.assertNotIn("\x1b", result)

        result = run_command("test_command1", "delete", "Brian", "--throw")[1]
        self.assertNotIn("\x1b", result)


@pytest.mark.no_rich
@pytest.mark.skipif(rich_installed, reason="rich installed")
class TestTracebackConfigNoRich(TestTracebackConfig):
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
            self.assertTrue("───── locals ─────" in stderr)
        else:
            self.assertFalse("───── locals ─────" in stderr)
        self.assertTrue("No such command 'wrong'" in stderr)
        self.assertTrue(retcode > 0)

        stdout, stderr, retcode = run_command(
            "tb", "--no-color", "--traceback", "error", "wrong"
        )
        self.assertFalse(stdout.strip())
        self.assertTrue("Traceback" in stderr)
        if rich_installed:
            self.assertTrue("───── locals ─────" in stderr)
        else:
            self.assertFalse("───── locals ─────" in stderr)
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
