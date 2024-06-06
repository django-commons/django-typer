import os
import re
from io import StringIO

import pytest
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import manage_py, run_command


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

    def test_help_precedence10(self):
        buffer = StringIO()
        cmd = get_command("help_precedence10", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence10")
        self.assertIn("Class docstring.", buffer.getvalue())

    def test_help_precedence11(self):
        buffer = StringIO()
        cmd = get_command("help_precedence11", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence11")
        self.assertIn("This docstring overrides base docstring.", buffer.getvalue())

    def test_help_precedence12(self):
        buffer = StringIO()
        cmd = get_command("help_precedence12", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence12")
        self.assertIn("Class docstring.", buffer.getvalue())

    def test_help_precedence13(self):
        buffer = StringIO()
        cmd = get_command("help_precedence13", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence13")
        self.assertIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )
        self.assertNotIn("Override higher precedence inherit.", buffer.getvalue())

    def test_help_precedence14(self):
        buffer = StringIO()
        cmd = get_command("help_precedence14", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence14")
        self.assertIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )
        self.assertNotIn("Override higher precedence inherit.", buffer.getvalue())

    def test_help_precedence15(self):
        buffer = StringIO()
        cmd = get_command("help_precedence15", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence15")
        self.assertNotIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )
        self.assertIn("Now class docstring is used!", buffer.getvalue())

    def test_help_precedence16(self):
        buffer = StringIO()
        cmd = get_command("help_precedence16", stdout=buffer, no_color=True)
        cmd.print_help("./manage.py", "help_precedence16")
        self.assertNotIn(
            "Test minimal TyperCommand subclass - typer param", buffer.getvalue()
        )
        self.assertIn("Now class docstring is used!", buffer.getvalue())

    @pytest.mark.skip()
    def test_help_from_other_dir(self):
        """
        This test is for coverage that the help ouput resolves the correct script when
        called from a non-relative path.

        TODO - running from another directory screws up the code coverage b/c relative
        paths. Fix this.
        """
        cwd = os.getcwd()
        try:
            os.chdir("./django_typer/tests")
            stdout, _, retcode = run_command(
                "help_precedence9", "--no-color", "--help", chdir=False
            )
            self.assertEqual(retcode, 0)
            self.assertIn("Class docstring.", stdout)
            self.assertIn(f"Usage: {manage_py}", stdout)
        finally:
            os.chdir(cwd)


class TestNativeHelpPrecedence(TestCase):
    def test_help_precedence_native1(self):
        buffer = StringIO()
        cmd = get_command("help_precedence_native1", no_color=True, stdout=buffer)
        cmd.print_help("./manage.py", "help_precedence_native1")
        self.assertIn("1: Command help", buffer.getvalue())

    def test_help_precedence_native2(self):
        buffer = StringIO()
        cmd = get_command("help_precedence_native2", no_color=True, stdout=buffer)
        cmd.print_help("./manage.py", "help_precedence_native2")
        self.assertIn("2: App help", buffer.getvalue())

    def test_help_precedence_native3(self):
        buffer = StringIO()
        cmd = get_command("help_precedence_native3", no_color=True, stdout=buffer)
        cmd.print_help("./manage.py", "help_precedence_native3")
        self.assertIn("3: Docstring help", buffer.getvalue())
