from django.test import TestCase
from django_typer import get_command


class TestDefaultCmdHowto(TestCase):
    cmd = "howto2"

    def test_default_howto(self):
        from django_typer.tests.apps.test_app.management.commands.howto2 import Command

        command = get_command(self.cmd, Command)
        self.assertEqual(command(), "handle")
        self.assertEqual(command.subcommand2(), "subcommand2")
        self.assertEqual(command.subcommand3(), "subcommand3")

        with self.assertRaises(Exception):
            command.handle()

        self.assertEqual(command.subcommand1(), "handle")


class TestDefaultCmdTyperHowto(TestDefaultCmdHowto):
    cmd = "howto2_typer"
