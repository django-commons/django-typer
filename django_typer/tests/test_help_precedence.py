import re
from io import StringIO
from django.test import TestCase

from django_typer import get_command


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
