import contextlib
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestChaining(TestCase):
    def test_command_chaining(self):
        result = run_command(
            "chain", "command1", "--option=one", "command2", "--option=two"
        )[0]
        self.assertEqual(
            result.splitlines(), "command1\ncommand2\n['one', 'two']\n".splitlines()
        )

        result = run_command(
            "chain", "command2", "--option=two", "command1", "--option=one"
        )[0]
        self.assertEqual(
            result.splitlines(), "command2\ncommand1\n['two', 'one']\n".splitlines()
        )

        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            result = call_command(
                "chain", "command2", "--option=two", "command1", "--option=one"
            )
        self.assertEqual(
            stdout.getvalue().splitlines(),
            "command2\ncommand1\n['two', 'one']\n".splitlines(),
        )
        self.assertEqual(result, ["two", "one"])

        chain = get_command("chain")
        self.assertEqual(chain.command1(option="one"), "one")
        self.assertEqual(chain.command2(option="two"), "two")
