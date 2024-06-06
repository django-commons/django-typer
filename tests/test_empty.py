from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class EmptyTests(TestCase):
    command = "empty"

    def test_empty_class_run(self):
        _, stderr, code = run_command(self.command)
        self.assertGreater(code, 0)
        self.assertTrue(
            f"NotImplementedError: No commands or command groups were registered on {self.command}"
            in stderr
        )

    def test_empty_class_call(self):
        with self.assertRaises(NotImplementedError):
            call_command(self.command)

    def test_empty_class_direct(self):
        with self.assertRaises(NotImplementedError):
            get_command(self.command)


class EmptyTyperTests(EmptyTests):
    command = "empty2"
