import contextlib
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestResultCallback(TestCase):
    def test_result_callback1(self):
        out = StringIO()
        call_command("result_callback1", "cmd", stdout=out)
        self.assertEqual(out.getvalue(), "finalized\n")

    def test_result_callback2(self):
        out = StringIO()
        call_command("result_callback2", "cmd1", "cmd2", stdout=out)
        self.assertEqual(out.getvalue(), "finalize\n")

    def test_result_callback3(self):
        out = StringIO()
        call_command("result_callback3", "cmd", stdout=out)
        self.assertEqual(out.getvalue(), "finalize\n")
