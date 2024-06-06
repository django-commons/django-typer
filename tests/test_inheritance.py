from django.test import TestCase

from tests.utils import run_command


class TestInheritance(TestCase):
    def test_handle_override(self):
        stdout, _, retcode = run_command("help_precedence8", "1", "2")
        self.assertEqual(retcode, 0)
        self.assertEqual(
            stdout,
            {
                "arg1": "1",
                "arg2": "2",
                "arg3": 0.5,
                "arg4": 1,
                "class": "<class 'tests.apps.test_app.management.commands.help_precedence8.Command'>",
            },
        )
        stdout, _, retcode = run_command("help_precedence16", "1", "2")
        self.assertEqual(retcode, 0)
        self.assertEqual(
            stdout,
            {
                "arg1": "1",
                "arg2": "2",
                "arg3": 0.5,
                "arg4": 1,
                "class": "<class 'tests.apps.test_app.management.commands.help_precedence16.Command'>",
            },
        )
