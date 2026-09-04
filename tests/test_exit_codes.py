from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command


class TestExitCodes(TestCase):
    """
    Regression tests for https://github.com/django-commons/django-typer/issues/318

    typer.Exit raised inside a command body must propagate as a real process exit
    code (SystemExit), not be swallowed into a return value that Django then
    prints to stdout while the process exits 0.
    """

    def test_call_command_propagates_exit_code(self):
        with self.assertRaises(SystemExit) as ctx:
            call_command("exit_code", code=3)
        self.assertEqual(ctx.exception.code, 3)

    def test_call_command_propagates_zero_exit_code(self):
        with self.assertRaises(SystemExit) as ctx:
            call_command("exit_code", code=0)
        self.assertEqual(ctx.exception.code, 0)

    def test_run_from_argv_propagates_exit_code(self):
        cmd = get_command("exit_code")
        with self.assertRaises(SystemExit) as ctx:
            cmd.run_from_argv(["manage.py", "exit_code", "--code", "5"])
        self.assertEqual(ctx.exception.code, 5)

    def test_chained_subcommand_exit_code_propagates(self):
        with self.assertRaises(SystemExit) as ctx:
            call_command("exit_code_chain", "a", "b", "--code", "2")
        self.assertEqual(ctx.exception.code, 2)
