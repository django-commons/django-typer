import contextlib
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestFinalize(TestCase):
    def test_finalize1(self):
        out = StringIO()
        call_command("finalize1", "cmd", stdout=out)
        self.assertEqual(out.getvalue(), "finalized\n")

    def test_finalize2(self):
        out = StringIO()
        call_command("finalize2", "cmd1", "cmd2", stdout=out)
        self.assertEqual(out.getvalue(), "finalize\n")

    def test_finalize3(self):
        out = StringIO()
        call_command("finalize3", "cmd", stdout=out)
        self.assertEqual(out.getvalue(), "finalize\n")

    def test_finalize_multi_kwargs_run(self):
        stdout, _, _ = run_command("finalize_multi_kwargs", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
        )

        stdout, _, _ = run_command("finalize_multi_kwargs", "cmd2", "3", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd2 3', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
        )

    def test_finalize_multi_kwargs_call(self):
        # todo - excluded common options should not appear?
        call_command("finalize_multi_kwargs", "cmd1")
        with contextlib.redirect_stdout(StringIO()) as out:
            call_command("finalize_multi_kwargs", "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
            )

            out.truncate(0)
            out.seek(0)

            call_command("finalize_multi_kwargs", "cmd2", "5", "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 5', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
            )

            out.truncate(0)
            out.seek(0)

            call_command(
                "finalize_multi_kwargs",
                "--traceback",
                "cmd2",
                "3",
                "cmd1",
                "--arg1",
                "2",
            )
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 3', 'cmd1 2'] | {'force_color': False, 'no_color': False, 'traceback': True}",
            )

    def test_finalize_multi_kwargs_obj(self):
        from tests.apps.test_app.management.commands.finalize_multi_kwargs import (
            Command,
        )

        out = StringIO()
        finalize4 = get_command("finalize_multi_kwargs", Command, stdout=out)
        self.assertEqual(
            finalize4.final([finalize4.cmd1(3), finalize4.cmd2(2)]).strip(),
            "finalized: ['cmd1 3', 'cmd2 2'] | {}",
        )

    def test_finalize5_run(self):
        stdout, _, _ = run_command("finalize5")
        self.assertEqual(stdout.strip(), "finalized: handle")

    def test_finalize5_call(self):
        out = StringIO()
        call_command("finalize5", stdout=out)
        self.assertEqual(out.getvalue().strip(), "finalized: handle")

    def test_finalize5_obj(self):
        from tests.apps.test_app.management.commands.finalize5 import Command

        out = StringIO()
        finalize5 = get_command("finalize5", Command, stdout=out)
        self.assertEqual(
            finalize5.final(finalize5()).strip(),
            "finalized: handle",
        )
