import json
from io import StringIO

import django
from django.core.management import call_command
from django.test import TestCase

from django_typer import get_command
from django_typer.tests.utils import run_command
from django_typer.utils import get_current_command


class BasicTests(TestCase):
    def test_common_options_function(self):
        from django_typer import _common_options

        self.assertIsNone(_common_options())

    def test_command_line(self):
        self.assertEqual(
            run_command("basic", "a1", "a2")[0],
            {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1},
        )

        self.assertEqual(
            run_command("basic", "a1", "a2", "--arg3", "0.75", "--arg4", "2")[0],
            {"arg1": "a1", "arg2": "a2", "arg3": 0.75, "arg4": 2},
        )

    def test_cmd_name(self):
        self.assertEqual(get_command("shellcompletion")._name, "shellcompletion")

    def test_call_command(self):
        out = StringIO()
        returned_options = json.loads(call_command("basic", ["a1", "a2"], stdout=out))
        self.assertEqual(
            returned_options, {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1}
        )

    def test_call_command_stdout(self):
        out = StringIO()
        call_command("basic", ["a1", "a2"], stdout=out)
        printed_options = json.loads(out.getvalue())
        self.assertEqual(
            printed_options, {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1}
        )

    def test_get_version(self):
        self.assertEqual(
            str(run_command("basic", "--version")[0]).strip(), django.get_version()
        )

    def test_call_direct(self):
        basic = get_command("basic")
        self.assertEqual(
            json.loads(basic.handle("a1", "a2")),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1},
        )

        from django_typer.tests.apps.test_app.management.commands.basic import (
            Command as Basic,
        )

        self.assertEqual(
            json.loads(Basic()("a1", "a2", arg3=0.75, arg4=2)),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.75, "arg4": 2},
        )

    def test_parser(self):
        basic_cmd = get_command("basic")
        parser = basic_cmd.create_parser("./manage.py", "basic")
        with self.assertRaises(NotImplementedError):
            parser.add_argument()

    def test_command_context(self):
        basic = get_command("basic")
        multi = get_command("multi")
        self.assertIsNone(get_current_command())
        with basic:
            self.assertEqual(basic, get_current_command())
            with basic:
                self.assertEqual(basic, get_current_command())
                with multi:
                    self.assertEqual(multi, get_current_command())
                self.assertEqual(basic, get_current_command())
            self.assertEqual(basic, get_current_command())
        self.assertIsNone(get_current_command())

    def test_renaming(self):
        self.assertEqual(run_command("rename", "default")[0].strip(), "handle")
        self.assertEqual(run_command("rename", "renamed")[0].strip(), "subcommand1")
        self.assertEqual(run_command("rename", "renamed2")[0].strip(), "subcommand2")

        self.assertEqual(call_command("rename", "default"), "handle")
        self.assertEqual(call_command("rename", "renamed"), "subcommand1")
        self.assertEqual(call_command("rename", "renamed2"), "subcommand2")

        self.assertEqual(get_command("rename")(), "handle")
        self.assertEqual(get_command("rename").subcommand1(), "subcommand1")
        self.assertEqual(get_command("rename").subcommand2(), "subcommand2")
