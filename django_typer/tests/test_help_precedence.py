import re
from io import StringIO
from django.test import TestCase
import os

from django_typer import get_command
from django_typer.tests.utils import run_command, manage_py
from pathlib import Path
import pytest


class TestHelpPrecedence(TestCase):
    def test_help_precedence1(self):
        buffer = StringIO()
        cmd = get_command("help_precedence1", no_color=True, stdout=buffer)
        cmd.print_help("./manage.py", "help_precedence1")
        self.assertTrue(
            re.search(
                r"help_precedence1\s+Test minimal TyperCommand subclass - command method",
                buffer.getvalue(),
            )
        )
        self.assertIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )

    def test_help_precedence2(self):
        buffer = StringIO()
        cmd = get_command("help_precedence2", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence2")
        self.assertIn(
            "Test minimal TyperCommand subclass - class member", buffer.getvalue()
        )
        self.assertTrue(
            re.search(
                r"help_precedence2\s+Test minimal TyperCommand subclass - command method",
                buffer.getvalue(),
            )
        )

    def test_help_precedence3(self):
        buffer = StringIO()
        cmd = get_command("help_precedence3", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence3")
        self.assertTrue(
            re.search(
                r"help_precedence3\s+Test minimal TyperCommand subclass - command method",
                buffer.getvalue(),
            )
        )
        self.assertIn(
            "Test minimal TyperCommand subclass - callback method", buffer.getvalue()
        )

    def test_help_precedence4(self):
        buffer = StringIO()
        cmd = get_command("help_precedence4", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence4")
        self.assertIn(
            "Test minimal TyperCommand subclass - callback docstring", buffer.getvalue()
        )
        self.assertTrue(
            re.search(
                r"help_precedence4\s+Test minimal TyperCommand subclass - command method",
                buffer.getvalue(),
            )
        )

    def test_help_precedence5(self):
        buffer = StringIO()
        cmd = get_command("help_precedence5", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence5")
        self.assertIn(
            "Test minimal TyperCommand subclass - command method", buffer.getvalue()
        )

    def test_help_precedence6(self):
        buffer = StringIO()
        cmd = get_command("help_precedence6", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence6")
        self.assertIn(
            "Test minimal TyperCommand subclass - docstring", buffer.getvalue()
        )

    def test_help_precedence7(self):
        buffer = StringIO()
        cmd = get_command("help_precedence7", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence7")
        self.assertIn(
            "Test minimal TyperCommand subclass - class member", buffer.getvalue()
        )

    def test_help_precedence8(self):
        buffer = StringIO()
        cmd = get_command("help_precedence8", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence8")
        self.assertIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )

    def test_help_precedence9(self):
        buffer = StringIO()
        cmd = get_command("help_precedence9", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence9")
        self.assertIn("Class docstring.", buffer.getvalue())

    @pytest.mark.skipif(
        not Path("/usr").exists(), reason="/usr directory does not exist!"
    )
    def test_help_from_other_dir(self):
        """
        This test is for coverage that the help ouput resolves the correct script when
        called from a non-relative path.
        """
        cwd = os.getcwd()
        os.chdir("/usr")
        stdout, _, retcode = run_command(
            "help_precedence9", "--no-color", "--help", chdir=False
        )
        self.assertEqual(retcode, 0)
        self.assertIn("Class docstring.", stdout)
        self.assertIn(f"Usage: {manage_py}", stdout)
        os.chdir(cwd)
