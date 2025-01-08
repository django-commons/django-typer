from io import StringIO

import pytest
from django.core.management import call_command
from django.test import TestCase, override_settings

from django_typer.management import get_command
from django_typer.management.commands.shellcompletion import Command as ShellComplete


class TestShellResolution(TestCase):
    """
    You must ensure the calling shell is the expected shell for each of these tests to pass.
    """

    def test_powershell(self):
        command = get_command("shellcompletion", ShellComplete)
        self.assertEqual(command.shell, "powershell")

    def test_pwsh(self):
        command = get_command("shellcompletion", ShellComplete)
        self.assertEqual(command.shell, "pwsh")

    def test_bash(self):
        command = get_command("shellcompletion", ShellComplete)
        self.assertEqual(command.shell, "bash")

    def test_zsh(self):
        command = get_command("shellcompletion", ShellComplete)
        self.assertEqual(command.shell, "zsh")

    def test_fish(self):
        command = get_command("shellcompletion", ShellComplete)
        self.assertEqual(command.shell, "fish")
