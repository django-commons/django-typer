import contextlib
import json
from decimal import Decimal
from io import StringIO
import re
import os
from pathlib import Path

from django.apps import apps
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from django_typer import get_command
from django_typer.tests.apps.examples.polls.models import Question
from django_typer.tests.apps.test_app.models import ShellCompleteTester
from django_typer.tests.utils import run_command


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
        from django_typer.tests.apps.examples.polls.models import Question

        parser = ModelObjectParser(Question)
        self.assertEqual(parser.convert(self.q1, None, None), self.q1)

    def test_app_label_parser_idempotency(self):
        from django_typer.parsers import parse_app_label

        poll_app = apps.get_app_config("django_typer_tests_apps_examples_polls")
        self.assertEqual(parse_app_label(poll_app), poll_app)

    def test_app_label_parser_completers(self):
        from django.apps import apps

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "completion django_typer.tests."
            )
        result = result.getvalue()
        self.assertTrue("django_typer.tests.apps.examples.polls" in result)
        self.assertTrue("django_typer.tests.apps.test_app" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "completion django_typer_tests")
        result = result.getvalue()
        self.assertTrue("django_typer_tests_apps_examples_polls" in result)
        self.assertTrue("django_typer_tests_apps_util" in result)

        self.assertEqual(
            json.loads(
                call_command("completion", "django_typer_tests_apps_examples_polls")
            ),
            ["django_typer_tests_apps_examples_polls"],
        )
        self.assertEqual(
            json.loads(
                call_command("completion", "django_typer.tests.apps.examples.polls")
            ),
            ["django_typer_tests_apps_examples_polls"],
        )

        with self.assertRaises(CommandError):
            call_command("completion", "django_typer_tests.polls")

        poll_app = apps.get_app_config("django_typer_tests_apps_examples_polls")
        test_app = apps.get_app_config("test_app")
        cmd = get_command("completion")
        self.assertEqual(
            json.loads(cmd([poll_app])),
            ["django_typer_tests_apps_examples_polls"],
        )

        self.assertEqual(
            json.loads(cmd(django_apps=[poll_app])),
            ["django_typer_tests_apps_examples_polls"],
        )

        self.assertEqual(
            json.loads(cmd(django_apps=[poll_app], option=test_app)),
            {
                "django_apps": ["django_typer_tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

        self.assertEqual(
            json.loads(
                call_command(
                    "completion",
                    "django_typer_tests_apps_examples_polls",
                    option=test_app,
                )
            ),
            {
                "django_apps": ["django_typer_tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

        self.assertEqual(
            json.loads(
                call_command(
                    "completion",
                    "django_typer_tests_apps_examples_polls",
                    "--option=test_app",
                )
            ),
            {
                "django_apps": ["django_typer_tests_apps_examples_polls"],
                "option": "test_app",
            },
        )

    def test_char_field(self):
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --char ja")
        result = result.getvalue()
        self.assertTrue("jack" in result)
        self.assertTrue("jason" in result)
        self.assertFalse("jon" in result)
        self.assertFalse("john" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --ichar Ja")
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
            call_command("shellcompletion", "complete", "model_fields test --ip ")
        result = result.getvalue()
        for ip in self.field_values["ip_field"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --ip 2001:")
        result = result.getvalue()
        for ip in ["2001::1"]:
            self.assertTrue(ip in result)

        # IP normalization complexity is unhandled
        # result = StringIO()
        # with contextlib.redirect_stdout(result):
        #     call_command("shellcompletion", "complete", "model_fields test --ip 2001:0")
        # result = result.getvalue()
        # self.assertFalse(result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --ip 2a02:42"
            )
        result = result.getvalue()
        for ip in ["2a02:42fe::4", "2a02:42ae::4"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --ip 2a02:42f"
            )
        result = result.getvalue()
        for ip in ["2a02:42fe::4"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --ip 192.")
        result = result.getvalue()
        for ip in ["192.168.1.1", "192.0.2.30"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --ip 192.1")
        result = result.getvalue()
        for ip in ["192.168.1.1"]:
            self.assertTrue(ip in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --ip :")
        result = result.getvalue()
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
            call_command("shellcompletion", "complete", "model_fields test --text ")
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
            call_command("shellcompletion", "complete", "model_fields test --text ch")
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
            call_command("shellcompletion", "complete", "model_fields test --itext S")
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

    def test_uuid_field(self):
        from uuid import UUID

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --uuid ")
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
                "shellcompletion", "complete", "model_fields test --uuid 12345678"
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
                "shellcompletion", "complete", "model_fields test --uuid 12345678-"
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
                "shellcompletion", "complete", "model_fields test --uuid 12345678-5"
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
                "shellcompletion", "complete", "model_fields test --uuid 123456785"
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
                "shellcompletion", "complete", "model_fields test --id ", shell="zsh"
            )

        result = result.getvalue()
        for id in ids:
            self.assertTrue(f'"{id}"' in result)

        for start_char in start_chars:
            expected = starts[start_char]
            unexpected = [str(id) for id in ids if str(id) not in expected]
            result = StringIO()
            with contextlib.redirect_stdout(result):
                call_command(
                    "shellcompletion",
                    "complete",
                    "--shell",
                    "zsh",
                    f"model_fields test --id {start_char}",
                )

            result = result.getvalue()
            for id in expected:
                self.assertTrue(f'"{id}"' in result)
            for id in unexpected:
                self.assertFalse(f'"{id}"' in result)

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
                "complete",
                "--shell",
                "zsh",
                "model_fields test --id-limit ",
            )
        result = result.getvalue()
        for id in ids[0:5]:
            self.assertTrue(f'"{id}"' in result)
        for id in ids[5:]:
            self.assertFalse(f'"{id}"' in result)

    def test_float_field(self):
        values = [1.1, 1.12, 2.2, 2.3, 2.4, 3.0, 4.0]
        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float ")
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 1")
        result = result.getvalue()
        for value in [1.1, 1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.1, 1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 1.1")
        result = result.getvalue()
        for value in [1.1, 1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.1, 1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --float 1.12"
            )
        result = result.getvalue()
        for value in [1.12]:
            self.assertTrue(str(value) in result)
        for value in set([1.12]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 2")
        result = result.getvalue()
        for value in [2.2, 2.3, 2.4]:
            self.assertTrue(str(value) in result)
        for value in set([2.2, 2.3, 2.4]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 2.")
        result = result.getvalue()
        for value in [2.2, 2.3, 2.4]:
            self.assertTrue(str(value) in result)
        for value in set([2.2, 2.3, 2.4]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 2.3")
        result = result.getvalue()
        for value in [2.3]:
            self.assertTrue(str(value) in result)
        for value in set([2.3]) - set(values):
            self.assertFalse(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "model_fields test --float 3")
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
            call_command("shellcompletion", "complete", "model_fields test --decimal ")
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --decimal 1."
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --decimal 1."
            )
        result = result.getvalue()
        for value in values:
            self.assertTrue(str(value) in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command(
                "shellcompletion", "complete", "model_fields test --decimal 1.5"
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
            call_command("shellcompletion", "complete", "model_fields test ")
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
            call_command("shellcompletion", "complete", "noarg cmd ", shell="zsh")
        result = result.getvalue()
        self.assertTrue(result)
        self.assertFalse("--" in result)

        result = StringIO()
        with contextlib.redirect_stdout(result):
            call_command("shellcompletion", "complete", "noarg cmd -", shell="zsh")
        result = result.getvalue()
        self.assertTrue(result)
        self.assertFalse("--" in result)

        # test what happens if we try to complete a non existing command
        with self.assertRaises(CommandError):
            call_command("shellcompletion", "complete", "noargs cmd ", shell="zsh")

    def test_unsupported_field(self):
        from django_typer.completers import ModelObjectCompleter

        with self.assertRaises(ValueError):
            ModelObjectCompleter(ShellCompleteTester, "binary_field")

    def test_shellcompletion_no_detection(self):
        from django_typer.management.commands import shellcompletion

        def raise_error():
            raise RuntimeError()

        shellcompletion.detect_shell = raise_error
        cmd = get_command("shellcompletion")
        with self.assertRaises(CommandError):
            cmd.shell = None

    def test_shellcompletion_complete_cmd(self):
        # test that we can leave preceeding script off the complete argument
        result = run_command(
            "shellcompletion", "complete", "./manage.py completion dj"
        )[0]
        self.assertTrue("django_typer" in result)
        result2 = run_command("shellcompletion", "complete", "completion dj")[0]
        self.assertTrue("django_typer" in result2)
        self.assertEqual(result, result2)

    def test_custom_fallback(self):
        result = run_command(
            "shellcompletion",
            "complete",
            "--fallback",
            "django_typer.tests.fallback.custom_fallback",
            "shell ",
        )[0]
        self.assertTrue("custom_fallback" in result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--fallback",
            "django_typer.tests.fallback.custom_fallback_cmd_str",
            "shell ",
        )[0]
        self.assertTrue("shell " in result)

    def test_import_path_completer(self):
        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --settings "
        )[0]
        self.assertIn('"importlib"', result)
        self.assertIn('"django_typer"', result)
        self.assertIn('"typer"', result)
        self.assertNotIn(".django_typer", result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --settings "
        )[0]
        self.assertIn('"importlib"', result)
        self.assertIn('"django_typer"', result)
        self.assertIn('"typer"', result)
        self.assertNotIn(".django_typer", result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --settings djan"
        )[0]
        self.assertNotIn('"importlib"', result)
        self.assertIn('"django"', result)
        self.assertIn('"django_typer"', result)
        self.assertNotIn('"typer"', result)
        self.assertNotIn(".django_typer", result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --settings django_ty",
        )[0]
        self.assertNotIn('"importlib"', result)
        self.assertNotIn('"typer"', result)
        self.assertNotIn(".django_typer", result)

        self.assertIn('"django_typer.completers"', result)
        self.assertIn('"django_typer.management"', result)
        self.assertIn('"django_typer.parsers"', result)
        self.assertIn('"django_typer.patch"', result)
        self.assertIn('"django_typer.tests"', result)
        self.assertIn('"django_typer.types"', result)
        self.assertIn('"django_typer.utils"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --settings django_typer.tests.settings.",
        )[0]
        self.assertNotIn('"importlib"', result)
        self.assertNotIn('"typer"', result)
        self.assertNotIn(".django_typer", result)
        settings_expected = [
            "django_typer.tests.settings.adapted",
            "django_typer.tests.settings.adapted1",
            "django_typer.tests.settings.adapted1_2",
            "django_typer.tests.settings.adapted2_1",
            "django_typer.tests.settings.base",
            "django_typer.tests.settings.examples",
            "django_typer.tests.settings.mod_init",
            "django_typer.tests.settings.override",
            "django_typer.tests.settings.settings2",
            "django_typer.tests.settings.settings_fail_check",
            "django_typer.tests.settings.settings_tb_bad_config",
            "django_typer.tests.settings.settings_tb_change_defaults",
            "django_typer.tests.settings.settings_tb_false",
            "django_typer.tests.settings.settings_tb_no_install",
            "django_typer.tests.settings.settings_tb_none",
            "django_typer.tests.settings.settings_throw_init_exception",
            "django_typer.tests.settings.typer_examples",
        ]
        for mod in settings_expected:
            self.assertIn(f'"{mod}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --settings django_typer.tests.settings.typer_examples",
        )[0]
        for mod in settings_expected[:-1]:
            self.assertNotIn(f'"{mod}"', result)

        self.assertIn(f'"{settings_expected[-1]}"', result)

    def test_pythonpath_completer(self):
        local_dirs = [pth for pth in os.listdir() if Path(pth).is_dir()]
        local_files = [f for f in os.listdir() if not Path(f).is_dir()]
        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --pythonpath "
        )[0]
        for pth in local_dirs:
            self.assertIn(f'"{pth}"', result)
        for pth in local_files:
            self.assertNotIn(f'"{pth}"', result)

        for incomplete in [".", "./"]:
            result = run_command(
                "shellcompletion",
                "complete",
                "--shell",
                "zsh",
                f"multi --pythonpath {incomplete}",
            )[0]
            for pth in local_dirs:
                self.assertIn(f'"./{pth}"', result)
            for pth in local_files:
                self.assertNotIn(f'"./{pth}"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --pythonpath ./d"
        )[0]
        self.assertIn('"./doc"', result)
        self.assertIn('"./django_typer"', result)
        for pth in [
            *local_files,
            *[pth for pth in local_dirs if not pth.startswith("d")],
        ]:
            self.assertNotIn(f'"./{pth}"', result)

        local_dirs = [
            str(Path("django_typer") / d)
            for d in os.listdir("django_typer")
            if (Path("django_typer") / d).is_dir()
        ]
        local_files = [
            str(Path("django_typer") / f)
            for f in os.listdir("django_typer")
            if not (Path("django_typer") / f).is_dir()
        ]
        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --pythonpath dj"
        )[0]
        for pth in local_dirs:
            self.assertIn(f'"{pth}"', result)
        for pth in local_files:
            self.assertNotIn(f'"{pth}"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --pythonpath ./dj"
        )[0]
        for pth in local_dirs:
            self.assertIn(f'"./{pth}"', result)
        for pth in local_files:
            self.assertNotIn(f'"./{pth}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath ./django_typer",
        )[0]
        self.assertIn('"./django_typer/management"', result)
        self.assertIn('"./django_typer/tests"', result)
        self.assertNotIn('"./django_typer/__init__.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath django_typer/",
        )[0]
        self.assertIn('"django_typer/management"', result)
        self.assertIn('"django_typer/tests"', result)
        self.assertNotIn('"django_typer/__init__.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath django_typer/man",
        )[0]
        self.assertIn('"django_typer/management/commands"', result)
        self.assertNotIn('"django_typer/examples"', result)
        self.assertNotIn('"django_typer/tests"', result)
        self.assertNotIn('"django_typer/management/__init__.py"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "multi --pythonpath /"
        )[0]
        for pth in os.listdir("/"):
            if Path(f"/{pth}").is_dir():
                self.assertIn(f'"/{pth}"', result)
            else:
                self.assertNotIn(f'"/{pth}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath django_typer/completers.py",
        )
        self.assertNotIn('"django_typer/completers.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath django_typer/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "multi --pythonpath does_not_exist/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

    def test_path_completer(self):
        local_paths = [pth for pth in os.listdir()]
        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path "
        )[0]
        for pth in local_paths:
            self.assertIn(f'"{pth}"', result)

        for incomplete in [".", "./"]:
            result = run_command(
                "shellcompletion",
                "complete",
                "--shell",
                "zsh",
                f"completion --path {incomplete}",
            )[0]
            for pth in local_paths:
                self.assertIn(f'"./{pth}"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path ./d"
        )[0]
        self.assertIn('"./doc"', result)
        self.assertIn('"./django_typer"', result)
        for pth in [
            *[pth for pth in local_paths if not pth.startswith("d")],
        ]:
            self.assertNotIn(f'"./{pth}"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path ./p"
        )[0]
        for pth in [
            *[pth for pth in local_paths if not pth.startswith("p")],
        ]:
            self.assertNotIn(f'"./{pth}"', result)

        local_paths = [
            str(Path("django_typer") / d)
            for d in os.listdir("django_typer")
            if (Path("django_typer") / d).is_dir()
        ]
        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path dj"
        )[0]
        for pth in local_paths:
            self.assertIn(f'"{pth}"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path ./dj"
        )[0]
        for pth in local_paths:
            self.assertIn(f'"./{pth}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path ./django_typer",
        )[0]
        self.assertIn('"./django_typer/management"', result)
        self.assertIn('"./django_typer/tests"', result)
        self.assertIn('"./django_typer/__init__.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path django_typer/",
        )[0]
        self.assertIn('"django_typer/management"', result)
        self.assertIn('"django_typer/tests"', result)
        self.assertIn('"django_typer/__init__.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path django_typer/man",
        )[0]
        self.assertIn('"django_typer/management/__init__.py"', result)
        self.assertIn('"django_typer/management/commands"', result)
        self.assertNotIn('"django_typer/examples"', result)
        self.assertNotIn('"django_typer/tests"', result)

        result = run_command(
            "shellcompletion", "complete", "--shell", "zsh", "completion --path /"
        )[0]
        for pth in os.listdir("/"):
            self.assertIn(f'"/{pth}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path django_typer/completers.py",
        )[0]
        self.assertIn('"django_typer/completers.py"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path django_typer/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --path does_not_exist/does_not_exist",
        )[0]
        self.assertNotIn("django_typer", result)

    def test_these_strings_completer(self):
        for opt in ["--str", "--dup"]:
            result = run_command(
                "shellcompletion", "complete", "--shell", "zsh", f"completion {opt} "
            )[0]
            for s in ["str1", "str2", "ustr"]:
                self.assertIn(f'"{s}"', result)

            result = run_command(
                "shellcompletion", "complete", "--shell", "zsh", f"completion {opt} s"
            )[0]
            self.assertNotIn(f'"ustr"', result)
            for s in ["str1", "str2"]:
                self.assertIn(f'"{s}"', result)

            result = run_command(
                "shellcompletion", "complete", "--shell", "zsh", f"completion {opt} str"
            )[0]
            self.assertNotIn(f'"ustr"', result)
            for s in ["str1", "str2"]:
                self.assertIn(f'"{s}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --str str1 --str ",
        )[0]
        self.assertNotIn(f'"str1"', result)
        for s in ["str2", "ustr"]:
            self.assertIn(f'"{s}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --dup str1 --dup ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f'"{s}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --str str1 --dup ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f'"{s}"', result)

        result = run_command(
            "shellcompletion",
            "complete",
            "--shell",
            "zsh",
            "completion --dup str1 --str ",
        )[0]
        for s in ["str1", "str2", "ustr"]:
            self.assertIn(f'"{s}"', result)

    def test_chain_and_commands_completer(self):
        result = run_command("shellcompletion", "complete", "completion --cmd dj")[
            0
        ].strip()

        self.assertTrue("django" in result)
        self.assertTrue("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)

        result = run_command(
            "shellcompletion", "complete", "completion --cmd django_typer --cmd dj"
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertFalse("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)

        result = run_command(
            "shellcompletion",
            "complete",
            "completion --cmd-dup django_typer --cmd-dup dj",
        )[0].strip()

        self.assertTrue("django" in result)
        self.assertTrue("django_typer" in result)

        self.assertTrue("dj_params1" in result)
        self.assertTrue("dj_params2" in result)
        self.assertTrue("dj_params3" in result)
        self.assertTrue("dj_params4" in result)
