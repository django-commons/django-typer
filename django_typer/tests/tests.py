import json
import subprocess
import sys
from io import StringIO
from pathlib import Path

import django
from django.core.management import call_command
from django.test import TestCase

manage_py = Path(__file__).parent.parent.parent / 'manage.py'


def run_command(command, *args):

    result = subprocess.run(
        [sys.executable, manage_py, command, *args],
        capture_output=True,
        text=True
    )

    # Check the return code to ensure the script ran successfully
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    # Parse the output
    if result.stdout:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout


class BasicTests(TestCase):

    def test_command_line(self):
        self.assertEqual(
            run_command('basic', 'a1', 'a2'),
            {'arg1': 'a1', 'arg2': 'a2', 'arg3': 0.5, 'arg4': 1}
        )

        self.assertEqual(
            run_command('basic', 'a1', 'a2', '--arg3', '0.75', '--arg4', '2'),
            {'arg1': 'a1', 'arg2': 'a2', 'arg3': 0.75, 'arg4': 2}
        )

    def test_call_command(self):
        out = StringIO()
        returned_options = json.loads(call_command('basic', ['a1', 'a2'], stdout=out))
        self.assertEqual(returned_options, {'arg1': 'a1', 'arg2': 'a2', 'arg3': 0.5, 'arg4': 1})

    def test_call_command_stdout(self):
        out = StringIO()
        call_command('basic', ['a1', 'a2'], stdout=out)
        printed_options = json.loads(out.getvalue())
        self.assertEqual(printed_options, {'arg1': 'a1', 'arg2': 'a2', 'arg3': 0.5, 'arg4': 1})

    def test_get_version(self):
        self.assertEqual(
            run_command('basic', '--version').strip(),
            django.get_version()
        )
