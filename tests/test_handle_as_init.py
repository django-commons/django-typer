from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestHandleAsInit(TestCase):
    def test_handle_as_init_run(self):
        stdout, stderr, retcode = run_command("handle_as_init")
        self.assertTrue("handle" in stdout)
        self.assertFalse(stderr.strip())
        self.assertEqual(retcode, 0)

        stdout, stderr, retcode = run_command("handle_as_init", "subcommand")
        self.assertTrue("subcommand" in stdout)
        self.assertFalse(stderr.strip())
        self.assertEqual(retcode, 0)

    def test_handle_as_init_call(self):
        self.assertEqual(call_command("handle_as_init").strip(), "handle")
        self.assertEqual(
            call_command("handle_as_init", "subcommand").strip(), "subcommand"
        )

    def test_handle_as_init_direct(self):
        self.assertEqual(get_command("handle_as_init")(), "handle")
        self.assertEqual(get_command("handle_as_init", "subcommand")(), "subcommand")
        self.assertEqual(get_command("handle_as_init").subcommand(), "subcommand")
