import contextlib
import json
import os
import re
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.apps import apps
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from django_typer.management.commands.shellcompletion import DETECTED_SHELL
from django_typer.management import get_command
from tests.apps.examples.polls.models import Question
from tests.apps.test_app.models import ShellCompleteTester
from tests.utils import run_command

SHELL = {
    "zsh": "zsh",
    "bash": "bash",
    "pwsh": "pwsh",
    "powershell": "powershell",
    "fish": "fish",
}.get(DETECTED_SHELL, "bash")


def get_values(completion):
    if SHELL == "zsh":
        return completion.split("\n")[1::3]
    elif SHELL == "bash":
        return [line.split(",")[1] for line in completion.split("\n") if line]
    elif SHELL in ["pwsh", "powershell"]:
        return [line.split(":::")[1] for line in completion.splitlines() if line]
    elif SHELL == "fish":
        raise NotImplementedError("Fish completion not implemented")
    raise NotImplementedError(f"get_values for shell {SHELL} not implemented")


class TestShellCompletersAndParsers(TestCase):
    field_values = {
        "char_field": ["jon", "john", "jack", "jason"],
        "text_field": [
            "sockeye",
            "chinook",
            "steelhead",
            "coho",
            "atlantic",
            "pink",
            "chum",
        ],
        "float_field": [1.1, 1.12, 2.2, 2.3, 2.4, 3.0, 4.0],
        "decimal_field": [
            Decimal("1.5"),
            Decimal("1.50"),
            Decimal("1.51"),
            Decimal("1.52"),
            Decimal("1.2"),
            Decimal("1.6"),
        ],
        "uuid_field": [
            "12345678-1234-5678-1234-567812345678",
            "12345678-1234-5678-1234-567812345679",
            "12345678-5678-5678-1234-567812345670",
            "12345678-5678-5678-1234-567812345671",
            "12345678-5678-5678-1234-A67812345671",
            "12345678-5678-5678-f234-A67812345671",
        ],
        "ip_field": [
            "192.168.1.1",
            "192.0.2.30",
            "10.0.0.1",
            "2a02:42fe::4",
            "2a02:42ae::4",
            #'2001:0::0:01', this gets normalized to the one below
            "2001::1",
            "::ffff:10.10.10.10",
        ],
    }

    def setUp(self):
        super().setUp()
        self.q1 = Question.objects.create(
            question_text="Is Putin a war criminal?",
            pub_date=timezone.now(),
        )
        for field, values in self.field_values.items():
            for value in values:
                ShellCompleteTester.objects.create(**{field: value})

    def tearDown(self) -> None:
        ShellCompleteTester.objects.all().delete()
        return super().tearDown()

    def test_model_object_parser_metavar(self):
        result = run_command("model_fields", "--no-color", "test", "--help")[0]
        self.assertTrue(re.search(r"--char\s+TXT", result))
        self.assertTrue(re.search(r"--ichar\s+TXT", result))
        self.assertTrue(re.search(r"--text\s+TXT", result))
        self.assertTrue(re.search(r"--itext\s+TXT", result))
        self.assertTrue(re.search(r"--uuid\s+UUID", result))
        self.assertTrue(re.search(r"--id\s+INT", result))
        self.assertTrue(re.search(r"--id-limit\s+INT", result))
        self.assertTrue(re.search(r"--float\s+FLOAT", result))
        self.assertTrue(re.search(r"--decimal\s+FLOAT", result))
        self.assertTrue(re.search(r"--ip\s+\[IPV4\|IPV6\]", result))
        self.assertTrue(re.search(r"--email\s+EMAIL", result))
        self.assertTrue(re.search(r"--url\s+URL", result))

    def test_model_object_parser_metavar_override(self):
        result = run_command("poll_as_option", "--help", "--no-color")[0]
        self.assertTrue(re.search(r"--polls\s+POLL", result))

    def test_model_object_parser_idempotency(self):
        from django_typer.parsers import ModelObjectParser
        from tests.apps.examples.polls.models import Question

        parser = ModelObjectParser(Question)
        self.assertEqual(parser.convert(self.q1, None, None), self.q1)

    def test_app_label_parser_idempotency(self):
        from django_typer.parsers import parse_app_label

        poll_app = apps.get_app_config("tests_apps_examples_polls")
        self.assertEqual(parse_app_label(poll_app), poll_app)

    def test_shellcompletion_stdout(self):
        from django_typer.management.commands.shellcompletion import (
            Command as ShellCompletion,
        )

        shellcompletion = get_command("shellcompletion", ShellCompletion)
        shellcompletion.init(shell=SHELL)
        result = shellcompletion.complete("completion ")
        self.assertTrue("test_app" in result)
        self.assertTrue("tests_apps_util" in result)
        self.assertTrue("django_typer" in result)

        result2 = StringIO()
        call_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion ",
            stdout=result2,
        )
        stdout_result = result2.getvalue().strip()
        self.assertTrue("test_app" in stdout_result)
        self.assertTrue("tests_apps_util" in stdout_result)
        self.assertTrue("django_typer" in stdout_result)

    def test_app_label_parser_completers(self):
        from django.apps import apps

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "--shell", SHELL, "complete", "completion ")
        result = result.getvalue()
        self.assertTrue("test_app" in result)
        self.assertTrue("tests_apps_util" in result)
        self.assertTrue("django_typer" in result)
        self.assertTrue("tests_apps_examples_polls" in result)
        self.assertTrue("admin" in result)
        self.assertTrue("auth" in result)
        self.assertTrue("contenttypes" in result)
        self.assertTrue("sessions" in result)
        self.assertTrue("messages" in result)
        self.assertTrue("staticfiles" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "completion --app-opt ",
            )
        result = result.getvalue()
        self.assertTrue("test_app" in result)
        self.assertTrue("tests_apps_util" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "--shell", SHELL, "complete", "completion tests."
            )
        result = result.getvalue()
        self.assertTrue("tests.apps.examples.polls" in result)
        self.assertTrue("tests.apps.test_app" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "--shell", SHELL, "complete", "completion tests"
            )
        result = result.getvalue()
        self.assertTrue("tests_apps_examples_polls" in result)
        self.assertTrue("tests_apps_util" in result)

        self.assertEqual(
            json.loads(call_command("completion", "tests_apps_examples_polls")),
            ["tests_apps_examples_polls"],
        )
        self.assertEqual(
            json.loads(call_command("completion", "tests.apps.examples.polls")),
            ["tests_apps_examples_polls"],
        )

        with self.assertRaises(CommandError):
            call_command("completion", "tests.polls")

        poll_app = apps.get_app_config("tests_apps_examples_polls")
        test_app = apps.get_app_config("test_app")
        cmd = get_command("completion")
        self.assertEqual(
            json.loads(cmd([poll_app])),
            ["tests_apps_examples_polls"],
        )

        self.assertEqual(
            json.loads(cmd(django_apps=[poll_app])),
            ["tests_apps_examples_polls"],
        )

        self.assertEqual(
            json.loads(cmd(django_apps=[poll_app], option=test_app)),
            {
                "django_apps": ["tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

        self.assertEqual(
            json.loads(
                call_command(
                    "completion",
                    "tests_apps_examples_polls",
                    option=test_app,
                )
            ),
            {
                "django_apps": ["tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

        self.assertEqual(
            json.loads(
                call_command(
                    "completion",
                    "tests_apps_examples_polls",
                    "--option=test_app",
                )
            ),
            {
                "django_apps": ["tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

    def test_char_field(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --char ja",
            )
        result = result.getvalue()
        self.assertTrue("jack" in result)
        self.assertTrue("jason" in result)
        self.assertFalse("jon" in result)
        self.assertFalse("john" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ichar Ja",
            )
        result = result.getvalue()
        self.assertTrue("Jack" in result)
        self.assertTrue("Jason" in result)
        self.assertFalse("Jon" in result)
        self.assertFalse("John" in result)

        self.assertEqual(
            json.loads(call_command("model_fields", "test", "--char", "jack")),
            {
                "char": {
                    str(ShellCompleteTester.objects.get(char_field="jack").pk): "jack"
                }
            },
        )

        self.assertEqual(
            json.loads(call_command("model_fields", "test", "--ichar", "john")),
            {
                "ichar": {
                    str(ShellCompleteTester.objects.get(char_field="john").pk): "john"
                }
            },
        )

        with self.assertRaises(CommandError):
            call_command("model_fields", "test", "--char", "jane")

        with self.assertRaises(RuntimeError):
            call_command("model_fields", "test", "--ichar", "jane")

    def test_ip_field(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip ",
            )
        result = result.getvalue().replace("\\", "")
        for ip in self.field_values["ip_field"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip 2001:",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["2001::1"]:
            self.assertTrue(ip in result)

        # IP normalization complexity is unhandled
        # result = StringIO()
        # with contextlib.redirect_stdout(result):
        #     call_command("shellcompletion", "--shell", SHELL, "complete", "model_fields test --ip 2001:0")
        # result = result.getvalue()
        # self.assertFalse(result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip 2a02:42",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["2a02:42fe::4", "2a02:42ae::4"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip 2a02:42f",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["2a02:42fe::4"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip 192.",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["192.168.1.1", "192.0.2.30"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip 192.1",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["192.168.1.1"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --ip :",
            )
        result = result.getvalue().replace("\\", "")
        for ip in ["::ffff:10.10.10.10"]:
            self.assertTrue(ip in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields", "test", "--ip", "2001:0::0:01", "--ip", "192.0.2.30"
                )
            ),
            {
                "ip": [
                    {
                        str(
                            ShellCompleteTester.objects.get(ip_field="2001:0::0:01").pk
                        ): "2001::1"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(ip_field="192.0.2.30").pk
                        ): "192.0.2.30"
                    },
                ]
            },
        )

    def test_text_field(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --text ",
            )
        result = result.getvalue()
        self.assertTrue("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertTrue("steelhead" in result)
        self.assertTrue("coho" in result)
        self.assertTrue("atlantic" in result)
        self.assertTrue("pink" in result)
        self.assertTrue("chum" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --text ch",
            )
        result = result.getvalue()
        self.assertFalse("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertFalse("steelhead" in result)
        self.assertFalse("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertFalse("pink" in result)
        self.assertTrue("chum" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --itext S",
            )
        result = result.getvalue()
        self.assertTrue("Sockeye" in result)
        self.assertFalse("chinook" in result)
        self.assertTrue("Steelhead" in result)
        self.assertFalse("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertFalse("pink" in result)
        self.assertFalse("chum" in result)

        # distinct completions by default
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --text atlantic --text sockeye --text steelhead --text ",
            )
        result = result.getvalue()
        self.assertFalse("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertFalse("steelhead" in result)
        self.assertTrue("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertTrue("pink" in result)
        self.assertTrue("chum" in result)

        # check distinct flag set to False
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --itext atlantic --itext sockeye --itext steelhead --itext ",
            )
        result = result.getvalue()
        self.assertTrue("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertTrue("steelhead" in result)
        self.assertTrue("coho" in result)
        self.assertTrue("atlantic" in result)
        self.assertTrue("pink" in result)
        self.assertTrue("chum" in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--text",
                    "atlantic",
                    "--text",
                    "sockeye",
                    "--text",
                    "steelhead",
                )
            ),
            {
                "text": [
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="atlantic").pk
                        ): "atlantic"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="sockeye").pk
                        ): "sockeye"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="steelhead").pk
                        ): "steelhead"
                    },
                ]
            },
        )
        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--itext",
                    "ATlanTIC",
                    "--itext",
                    "SOCKeye",
                    "--itext",
                    "STEELHEAD",
                )
            ),
            {
                "itext": [
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="atlantic").pk
                        ): "atlantic"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="sockeye").pk
                        ): "sockeye"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="steelhead").pk
                        ): "steelhead"
                    },
                ]
            },
        )

    def test_filtered_text_field(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --filtered ",
            )
        result = result.getvalue()
        self.assertFalse("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertFalse("steelhead" in result)
        self.assertTrue("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertTrue("pink" in result)
        self.assertTrue("chum" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --filtered ch",
            )
        result = result.getvalue()
        self.assertFalse("sockeye" in result)
        self.assertTrue("chinook" in result)
        self.assertFalse("steelhead" in result)
        self.assertFalse("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertFalse("pink" in result)
        self.assertTrue("chum" in result)

        # distinct completions by default
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --filtered coho --filtered chinook --filtered ",
            )
        result = result.getvalue()
        self.assertFalse("sockeye" in result)
        self.assertFalse("chinook" in result)
        self.assertFalse("steelhead" in result)
        self.assertFalse("coho" in result)
        self.assertFalse("atlantic" in result)
        self.assertTrue("pink" in result)
        self.assertTrue("chum" in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--filtered",
                    "coho",
                    "--filtered",
                    "chinook",
                )
            ),
            {
                "filtered": [
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="coho").pk
                        ): "coho"
                    },
                    {
                        str(
                            ShellCompleteTester.objects.get(text_field="chinook").pk
                        ): "chinook"
                    },
                ]
            },
        )

    def test_uuid_field(self):
        from uuid import UUID

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid ",
            )
        result = result.getvalue()
        self.assertTrue("12345678-1234-5678-1234-567812345678" in result)
        self.assertTrue("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345670" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345671" in result)
        self.assertTrue("12345678-5678-5678-1234-a67812345671" in result)
        self.assertTrue("12345678-5678-5678-f234-a67812345671" in result)
        self.assertFalse("None" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 12345678",
            )
        result = result.getvalue()
        self.assertTrue("12345678-1234-5678-1234-567812345678" in result)
        self.assertTrue("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345670" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345671" in result)
        self.assertTrue("12345678-5678-5678-1234-a67812345671" in result)
        self.assertTrue("12345678-5678-5678-f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 12345678-",
            )
        result = result.getvalue()
        self.assertTrue("12345678-1234-5678-1234-567812345678" in result)
        self.assertTrue("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345670" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345671" in result)
        self.assertTrue("12345678-5678-5678-1234-a67812345671" in result)
        self.assertTrue("12345678-5678-5678-f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 12345678-5",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345670" in result)
        self.assertTrue("12345678-5678-5678-1234-567812345671" in result)
        self.assertTrue("12345678-5678-5678-1234-a67812345671" in result)
        self.assertTrue("12345678-5678-5678-f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 123456785",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("123456785678-5678-1234-567812345670" in result)
        self.assertTrue("123456785678-5678-1234-567812345671" in result)
        self.assertTrue("123456785678-5678-1234-a67812345671" in result)
        self.assertTrue("123456785678-5678-f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 123456&78-^56785678-",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertTrue("123456&78-^56785678-1234-567812345670" in result)
        self.assertTrue("123456&78-^56785678-1234-567812345671" in result)
        self.assertTrue("123456&78-^56785678-1234-a67812345671" in result)
        self.assertTrue("123456&78-^56785678-f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 123456&78-^56785678F",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertFalse("123456&78-^567856781234-567812345670" in result)
        self.assertFalse("123456&78-^567856781234-567812345671" in result)
        self.assertFalse("123456&78-^567856781234-a67812345671" in result)
        self.assertTrue("123456&78-^56785678F234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 123456&78-^56785678f",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertFalse("123456&78-^567856781234-567812345670" in result)
        self.assertFalse("123456&78-^567856781234-567812345671" in result)
        self.assertFalse("123456&78-^567856781234-a67812345671" in result)
        self.assertTrue("123456&78-^56785678f234-a67812345671" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "--no-color",
                "complete",
                "model_fields test --uuid 123456&78-^56785678f234---A",
            )
        result = result.getvalue()
        self.assertFalse("12345678-1234-5678-1234-567812345678" in result)
        self.assertFalse("12345678-1234-5678-1234-567812345679" in result)
        self.assertFalse("123456&78-^567856781234-567812345670" in result)
        self.assertFalse("123456&78-^567856781234-567812345671" in result)
        self.assertFalse("123456&78-^567856781234-a67812345671" in result)
        self.assertTrue("123456&78-^56785678f234---A67812345671" in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--uuid",
                    "123456&78-^56785678f234---A67812345671",
                )
            ),
            {
                "uuid": {
                    str(
                        ShellCompleteTester.objects.get(
                            uuid_field=UUID("12345678-5678-5678-f234-a67812345671")
                        ).pk
                    ): "12345678-5678-5678-f234-a67812345671"
                }
            },
        )

        with self.assertRaises(CommandError):
            call_command(
                "model_fields", "test", "--uuid", "G2345678-5678-5678-f234-a67812345671"
            )

        with self.assertRaises(CommandError):
            call_command(
                "model_fields", "test", "--uuid", "12345678-5678-5678-f234-a67812345675"
            )

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --uuid 12345678-5678-5678-f234-a678123456755",
            )
        result = result.getvalue()
        self.assertFalse("12345678" in result)

    def test_id_field(self):
        result = StringIO()

        ids = ShellCompleteTester.objects.values_list("id", flat=True)

        starts = {}
        for id in ids:
            starts.setdefault(str(id)[0], []).append(str(id))
        start_chars = set(starts.keys())

        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --id ",
                shell=SHELL,
            )

        result = result.getvalue()
        for id in ids:
            self.assertTrue(f"{id}" in result)

        for start_char in start_chars:
            expected = starts[start_char]
            unexpected = [str(id) for id in ids if str(id) not in expected]
            result = StringIO()
            with contextlib.redirect_stdout(result):
                call_command(
                    "shellcompletion",
                    "--shell",
                    SHELL,
                    "complete",
                    f"model_fields test --id {start_char}",
                )

            result = result.getvalue()
            for comp in get_values(result):
                self.assertTrue(comp in expected)
                self.assertTrue(comp not in unexpected)

        for id in ids:
            self.assertEqual(
                json.loads(call_command("model_fields", "test", "--id", str(id))),
                {"id": id},
            )

        # test the limit option
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --id-limit ",
            )
        result = result.getvalue()
        for id in ids[0:5]:
            self.assertTrue(f"{id}" in result)
        for id in ids[5:]:
            self.assertFalse(f"{id}" in result)

    def test_float_field(self):
        values = [1.1, 1.12, 2.2, 2.3, 2.4, 3.0, 4.0]
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float ",
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 1",
            )
        result = result.getvalue()
        for value in [1.1, 1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.1, 1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 1.1",
            )
        result = result.getvalue()
        for value in [1.1, 1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.1, 1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 1.12",
            )
        result = result.getvalue()
        for value in [1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 2",
            )
        result = result.getvalue()
        for value in [2.2, 2.3, 2.4]:
            self.assertTrue(str(value) in result)
        for value in set([2.2, 2.3, 2.4]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 2.",
            )
        result = result.getvalue()
        for value in [2.2, 2.3, 2.4]:
            self.assertTrue(str(value) in result)
        for value in set([2.2, 2.3, 2.4]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 2.3",
            )
        result = result.getvalue()
        for value in [2.3]:
            self.assertTrue(str(value) in result)
        for value in set([2.3]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --float 3",
            )
        result = result.getvalue()
        for value in [3.0]:
            self.assertTrue(str(value) in result)
        for value in set([3.0]) - set(values):
            self.assertFalse(str(value) in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--float",
                    "2.3",
                )
            ),
            {
                "float": {
                    str(ShellCompleteTester.objects.get(float_field=2.3).pk): "2.3"
                }
            },
        )

    def test_decimal_field(self):
        values = [
            Decimal("1.5"),
            Decimal("1.50"),
            Decimal("1.51"),
            Decimal("1.52"),
            Decimal("1.2"),
            Decimal("1.6"),
        ]
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --decimal ",
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --decimal 1.",
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --decimal 1.",
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "model_fields test --decimal 1.5",
            )
        result = result.getvalue()
        for value in set(values) - {Decimal("1.2"), Decimal("1.6")}:
            self.assertTrue(str(value) in result)
        for value in {Decimal("1.2"), Decimal("1.6")}:
            self.assertFalse(str(value) in result)

        self.assertEqual(
            json.loads(
                call_command(
                    "model_fields",
                    "test",
                    "--decimal",
                    "1.6",
                )
            ),
            {
                "decimal": {
                    str(
                        ShellCompleteTester.objects.get(decimal_field=Decimal("1.6")).pk
                    ): "1.60"
                }
            },
        )

    def test_option_complete(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "--no-color",
                "complete",
                "model_fields test ",
            )
        result = result.getvalue()
        self.assertTrue("--char" in result)
        self.assertTrue("--ichar" in result)
        self.assertTrue("--text" in result)
        self.assertTrue("--itext" in result)
        self.assertTrue("--id" in result)
        self.assertTrue("--id-limit" in result)
        self.assertTrue("--float" in result)
        self.assertTrue("--decimal" in result)
        self.assertTrue("--help" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "noarg cmd ",
                shell=SHELL,
            )
        result = result.getvalue()
        self.assertFalse(result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "noarg cmd -",
                shell=SHELL,
            )
        result = result.getvalue()
        self.assertFalse(result)
        self.assertFalse("--" in result)

        # test what happens if we try to complete a non existing command
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "noargs cmd ",
                shell=SHELL,
            )
        result = result.getvalue()
        self.assertFalse(result)

    def test_unsupported_field(self):
        from django_typer.completers import ModelObjectCompleter

        with self.assertRaises(ValueError):
            ModelObjectCompleter(ShellCompleteTester, "binary_field")

    def test_shellcompletion_unsupported_shell(self):
        from django_typer.management.commands import shellcompletion

        def raise_error():
            raise RuntimeError()

        shellcompletion.detect_shell = raise_error
        cmd = get_command("shellcompletion")
        with self.assertRaises(CommandError):
            cmd.shell = "DNE"
            cmd.shell_class

    def test_shellcompletion_complete_cmd(self):
        # test that we can leave preceeding script off the complete argument
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "./manage.py completion dj"
        )[0]
        self.assertTrue("django_typer" in result)
        result2 = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion dj"
        )[0]
        self.assertTrue("django_typer" in result2)
        self.assertEqual(result, result2)

    def test_custom_fallback(self):
        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "--fallback",
            "tests.fallback.custom_fallback",
            "shell ",
        )[0]
        self.assertTrue("custom_fallback" in result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "--fallback",
            "tests.fallback.custom_fallback_cmd_str",
            "shell ",
        )[0]
        self.assertTrue("shell" in result)

        with self.assertRaises(CommandError):
            call_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                "--fallback",
                "tests.fallback.does_not_exist",
                "shell ",
            )

    def test_unknown_shell_error(self):
        from django_typer.management.commands.shellcompletion import (
            Command as ShellCompletion,
        )

        shellcompletion = get_command("shellcompletion", ShellCompletion)
        shellcompletion._shell = None
        with self.assertRaises(CommandError):
            shellcompletion.shell = None

    def test_import_path_completer(self):
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --settings "
        )[0]
        self.assertIn("importlib", result)
        self.assertIn("django_typer", result)
        self.assertIn("typer", result)
        self.assertNotIn(".django_typer", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --settings "
        )[0]
        self.assertIn("importlib", result)
        self.assertIn("django_typer", result)
        self.assertIn("typer", result)
        self.assertNotIn(".django_typer", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --settings djan"
        )[0]
        self.assertIn("django", result)
        self.assertIn("django_typer", result)
        for comp in get_values(result):
            self.assertTrue(comp.startswith("djan"), f"{comp} does not start with djan")

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --settings django_ty",
        )[0]
        self.assertNotIn("importlib", result)
        self.assertNotIn(".django_typer", result)
        for comp in get_values(result):
            self.assertTrue(
                comp.startswith("django_ty"), f"{comp} does not start with django_ty"
            )

        self.assertIn("django_typer.completers", result)
        self.assertIn("django_typer.management", result)
        self.assertIn("django_typer.parsers", result)
        self.assertIn("django_typer.patch", result)
        self.assertIn("django_typer.types", result)
        self.assertIn("django_typer.utils", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --settings tests.settings.",
        )[0]

        for comp in get_values(result):
            self.assertTrue(
                comp.startswith("tests.settings."),
                f"{comp} does not start with tests.settings.",
            )

        settings_expected = [
            "tests.settings.adapted",
            "tests.settings.adapted1",
            "tests.settings.adapted1_2",
            "tests.settings.adapted2_1",
            "tests.settings.base",
            "tests.settings.examples",
            "tests.settings.mod_init",
            "tests.settings.override",
            "tests.settings.settings2",
            "tests.settings.settings_fail_check",
            "tests.settings.settings_tb_bad_config",
            "tests.settings.settings_tb_change_defaults",
            "tests.settings.settings_tb_false",
            "tests.settings.settings_tb_no_install",
            "tests.settings.settings_tb_none",
            "tests.settings.settings_throw_init_exception",
            "tests.settings.typer_examples",
        ]
        for mod in settings_expected:
            self.assertIn(f"{mod}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --settings tests.settings.typer_examples",
        )[0]
        for mod in settings_expected[:-1]:
            self.assertNotIn(f"{mod}", result)

        self.assertIn(f"{settings_expected[-1]}", result)

    def test_pythonpath_completer(self):
        local_dirs = [
            Path(pth).as_posix() for pth in os.listdir() if Path(pth).is_dir()
        ]
        local_files = [Path(f).as_posix() for f in os.listdir() if not Path(f).is_dir()]
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --pythonpath "
        )[0]
        for pth in local_dirs:
            self.assertIn(f"{pth}", result)
        for pth in local_files:
            self.assertNotIn(f"{pth}", result)

        for incomplete, sep in [(".", os.path.sep), (".\\", "\\")]:
            result = run_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                f"multi --pythonpath '{incomplete}'",
            )[0]
            for pth in local_dirs:
                self.assertIn(f".{sep}{pth}", result)
            for pth in local_files:
                self.assertNotIn(f".{sep}{pth}", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --pythonpath ./d"
        )[0]
        self.assertIn("./doc", result)
        self.assertIn("./django_typer", result)
        for pth in [
            *local_files,
            *[pth for pth in local_dirs if not pth.startswith("d")],
        ]:
            self.assertNotIn(f"./{pth}", result)

        local_dirs = [
            (Path("django_typer") / d).as_posix()
            for d in os.listdir("django_typer")
            if (Path("django_typer") / d).is_dir()
        ]
        local_files = [
            (Path("django_typer") / f).as_posix()
            for f in os.listdir("django_typer")
            if not (Path("django_typer") / f).is_dir()
        ]
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --pythonpath dj"
        )[0]
        for pth in local_dirs:
            self.assertIn(pth.replace("/", os.path.sep), result)
        for pth in local_files:
            self.assertNotIn(pth.replace("/", os.path.sep), result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --pythonpath ./dj"
        )[0]
        for pth in local_dirs:
            self.assertIn(f"./{pth}", result)
        for pth in local_files:
            self.assertNotIn(f"./{pth}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath ./django_typer",
        )[0]
        self.assertIn("./django_typer/management", result)
        self.assertIn("./django_typer/locale", result)
        self.assertNotIn("./django_typer/__init__.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath django_typer/",
        )[0]
        self.assertIn("django_typer/management", result)
        self.assertIn("django_typer/locale", result)
        self.assertNotIn("django_typer/__init__.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath django_typer/man",
        )[0]
        self.assertIn("django_typer/management/commands", result)
        self.assertNotIn("django_typer/examples", result)
        self.assertNotIn("django_typer/locale", result)
        self.assertNotIn("django_typer/management/__init__.py", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "multi --pythonpath /"
        )[0]
        for pth in os.listdir("/"):
            if pth.startswith("$"):
                continue  # TODO weird case of /\\$Recycle.Bin on windows
            if Path(f"/{pth}").is_dir():
                self.assertIn(f"/{pth}", result)
            else:
                self.assertNotIn(f"/{pth}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath django_typer/completers.py",
        )
        self.assertNotIn("django_typer/completers.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath django_typer/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "multi --pythonpath does_not_exist/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

    def test_path_completer(self):
        local_paths = [Path(pth).as_posix() for pth in os.listdir()]
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path "
        )[0]
        for pth in local_paths:
            self.assertIn(f"{pth}", result)

        for incomplete, sep in [(".", os.path.sep), ("./", "/")]:
            result = run_command(
                "shellcompletion",
                "--shell",
                SHELL,
                "complete",
                f"completion --path {incomplete}",
            )[0]
            for pth in local_paths:
                self.assertIn(f".{sep}{pth}", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path ./d"
        )[0]
        self.assertIn("./doc", result)
        self.assertIn("./django_typer", result)
        for pth in [
            *[pth for pth in local_paths if not pth.startswith("d")],
        ]:
            self.assertNotIn(f"./{pth}", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path ./p"
        )[0]
        for pth in [
            *[pth for pth in local_paths if not pth.startswith("p")],
        ]:
            self.assertNotIn(f"./{pth}", result)

        local_paths = [
            (Path("django_typer") / d).as_posix()
            for d in os.listdir("django_typer")
            if (Path("django_typer") / d).is_dir()
        ]
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path dj"
        )[0]
        for pth in local_paths:
            self.assertIn(str(pth).replace("/", os.path.sep), result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path ./dj"
        )[0]
        for pth in local_paths:
            self.assertIn(f"./{pth}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path ./django_typer",
        )[0]
        self.assertIn("./django_typer/management", result)
        self.assertIn("./django_typer/locale", result)
        self.assertIn("./django_typer/__init__.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path django_typer/",
        )[0]
        self.assertIn("django_typer/management", result)
        self.assertIn("django_typer/locale", result)
        self.assertIn("django_typer/__init__.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path django_typer/man",
        )[0]
        self.assertIn("django_typer/management/__init__.py", result)
        self.assertIn("django_typer/management/commands", result)
        self.assertNotIn("django_typer/examples", result)
        self.assertNotIn("django_typer/locale", result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --path /"
        )[0]
        for pth in os.listdir("/"):
            if pth.startswith("$"):
                continue  # TODO weird case of /\\$Recycle.Bin on windows
            self.assertIn(f"/{pth}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path django_typer/completers.py",
        )[0]
        self.assertIn("django_typer/completers.py", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path django_typer/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --path does_not_exist/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

    def test_these_strings_completer(self):
        for opt in ["--str", "--dup"]:
            result = run_command(
                "shellcompletion", "--shell", SHELL, "complete", f"completion {opt} "
            )[0]
            for s in ["str1", "str2", "ustr"]:
                self.assertIn(f"{s}", result)

            result = run_command(
                "shellcompletion", "--shell", SHELL, "complete", f"completion {opt} s"
            )[0]
            self.assertNotIn("ustr", result)
            for s in ["str1", "str2"]:
                self.assertIn(f"{s}", result)

            result = run_command(
                "shellcompletion", "--shell", SHELL, "complete", f"completion {opt} str"
            )[0]
            self.assertNotIn("ustr", result)
            for s in ["str1", "str2"]:
                self.assertIn(f"{s}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --str str1 --str ",
        )[0]
        self.assertNotIn("str1", result)
        for s in ["str2", "ustr"]:
            self.assertIn(f"{s}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --dup str1 --dup ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f"{s}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --str str1 --dup ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f"{s}", result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --dup str1 --str ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f"{s}", result)

    def test_chain_and_commands_completer(self):
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --cmd dj"
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertTrue("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --cmd django_typer --cmd dj",
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertFalse("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)

        result = run_command(
            "shellcompletion",
            "--shell",
            SHELL,
            "complete",
            "completion --cmd-dup django_typer --cmd-dup dj",
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertTrue("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)

        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --cmd-first dj"
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertTrue("django_typer" in result)

        self.assertFalse("dj_params1" in result)
        self.assertFalse("dj_params2" in result)
        self.assertFalse("dj_params3" in result)
        self.assertFalse("dj_params4" in result)

    def test_databases_completer(self):
        result = run_command(
            "shellcompletion", "--shell", SHELL, "complete", "completion --db "
        )[0].strip()

        self.assertTrue("default" in result)

    def test_model_completer_argument_test(self):
        from django_typer.completers import ModelObjectCompleter

        class NotAModel:
            pass

        with self.assertRaises(ValueError):
            ModelObjectCompleter(NotAModel, "char_field", "test")
