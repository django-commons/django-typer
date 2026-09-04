"""
How typer.Exit, typer.Abort, KeyboardInterrupt and sys.exit leave a command.

From the command line the process ends with the corresponding status and nothing
extra is printed. From Python a non-zero Exit and an Abort become a CommandError
carrying the status as ``returncode``, and Exit(0) is simply success.
See https://github.com/django-commons/django-typer/issues/318
"""

import typer
from django.core.management import CommandError, call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class ExitPolicyTests(TestCase):
    def test_exit_status_from_the_command_line(self):
        for code in (0, 3):
            stdout, stderr, retcode = run_command(
                "exit_codes", "--no-color", "exit", "--code", str(code)
            )
            self.assertEqual(retcode, code, stderr)
            self.assertEqual(stdout.strip(), "")  # the code is not output
            self.assertEqual(stderr.strip(), "")

        stdout, stderr, retcode = run_command(
            "exit_codes_chain", "--no-color", "a", "b", "--code", "2"
        )
        self.assertEqual(retcode, 2, stderr)
        self.assertEqual(stdout.strip(), "a ran")

        stdout, stderr, retcode = run_command(
            "exit_codes_handle", "--no-color", "--code", "5"
        )
        self.assertEqual(retcode, 5, stderr)
        self.assertEqual(stdout.strip(), "")

    def test_exit_from_call_command(self):
        self.assertIsNone(call_command("exit_codes", "exit"))
        self.assertIsNone(call_command("exit_codes", "exit", "--code", "0"))
        self.assertIsNone(call_command("exit_codes_handle", code=0))

        with self.assertRaises(CommandError) as raised:
            call_command("exit_codes", "exit", "--code", "3")
        self.assertEqual(raised.exception.returncode, 3)
        self.assertIn("exited with code 3", str(raised.exception))
        self.assertIsInstance(raised.exception.__cause__, typer.Exit)

        with self.assertRaises(CommandError) as raised:
            call_command("exit_codes_chain", "a", "b", "--code", "2")
        self.assertEqual(raised.exception.returncode, 2)

        with self.assertRaises(CommandError) as raised:
            call_command("exit_codes_handle", code=5)
        self.assertEqual(raised.exception.returncode, 5)

    def test_exit_from_a_direct_call(self):
        cmd = get_command("exit_codes_handle")
        self.assertIsNone(cmd(code=0))
        with self.assertRaises(CommandError) as raised:
            cmd(code=4)
        self.assertEqual(raised.exception.returncode, 4)

    def test_abort(self):
        stdout, stderr, retcode = run_command("exit_codes", "--no-color", "abort")
        self.assertEqual(retcode, 1)
        self.assertEqual(stdout.strip(), "")
        self.assertEqual(stderr.strip(), "Aborted!")

        with self.assertRaises(CommandError) as raised:
            call_command("exit_codes", "abort")
        self.assertEqual(raised.exception.returncode, 1)
        self.assertEqual(str(raised.exception), "Aborted!")
        self.assertIsInstance(raised.exception.__cause__, typer.Abort)

    def test_end_of_input_at_a_prompt_aborts(self):
        self.assertEqual(run_command("exit_codes", "--no-color", "eof")[2], 1)
        with self.assertRaises(CommandError) as raised:
            call_command("exit_codes", "eof")
        self.assertEqual(str(raised.exception), "Aborted!")

    def test_keyboard_interrupt(self):
        stdout, stderr, retcode = run_command("exit_codes", "--no-color", "interrupt")
        self.assertEqual(retcode, 130)
        self.assertNotIn("Traceback", stderr)
        # a Python caller gets the interrupt itself, not a CommandError
        with self.assertRaises(KeyboardInterrupt):
            call_command("exit_codes", "interrupt")

    def test_sys_exit_is_unchanged(self):
        self.assertEqual(run_command("exit_codes", "sysexit", "--code", "4")[2], 4)
        with self.assertRaises(SystemExit):
            call_command("exit_codes", "sysexit", "--code", "4")

    def test_help_still_ends_the_process(self):
        stdout, stderr, retcode = run_command("exit_codes", "--no-color", "--help")
        self.assertEqual(retcode, 0)
        self.assertIn("Usage:", stdout)
        with self.assertRaises(SystemExit):
            call_command("exit_codes", "--help")
