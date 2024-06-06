from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestReturnValues(TestCase):
    """
    Tests that overloaded group/command names work as expected.
    """

    def test_return_direct(self):
        return_cmd = get_command("return")
        self.assertEqual(return_cmd(), {"key": "value"})

    def test_return_cli(self):
        self.assertEqual(run_command("return")[0].strip(), str({"key": "value"}))

    def test_return_call(self):
        self.assertEqual(call_command("return"), {"key": "value"})
