import inspect
import json
import subprocess
import sys
from io import StringIO
from pathlib import Path

import django
import typer
from django.core.management import call_command, get_commands, load_command_class
from django.test import TestCase

manage_py = Path(__file__).parent.parent.parent / "manage.py"


def get_named_arguments(function):
    sig = inspect.signature(function)
    return [
        name
        for name, param in sig.parameters.items()
        if param.default != inspect.Parameter.empty
    ]


def run_command(command, *args):
    result = subprocess.run(
        [sys.executable, manage_py, command, *args], capture_output=True, text=True
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
            run_command("basic", "a1", "a2"),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1},
        )

        self.assertEqual(
            run_command("basic", "a1", "a2", "--arg3", "0.75", "--arg4", "2"),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.75, "arg4": 2},
        )

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
            run_command("basic", "--version").strip(), django.get_version()
        )

    def test_call_direct(self):
        basic = load_command_class(get_commands()["basic"], "basic")
        self.assertEqual(
            json.loads(basic.handle("a1", "a2")),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.5, "arg4": 1},
        )

        from django_typer.tests.test_app.management.commands.basic import (
            Command as Basic,
        )

        self.assertEqual(
            json.loads(Basic()("a1", "a2", arg3=0.75, arg4=2)),
            {"arg1": "a1", "arg2": "a2", "arg3": 0.75, "arg4": 2},
        )


class InterfaceTests(TestCase):
    """
    Make sure the django_typer decorator inerfaces match the
    typer decorator interfaces. We don't simply pass variadic arguments
    to the typer decorator because we want the IDE to offer auto complete
    suggestions.
    """

    def test_command_interface_matches(self):
        from django_typer import command

        command_params = set(get_named_arguments(command))
        typer_params = set(get_named_arguments(typer.Typer.command))

        self.assertFalse(command_params.symmetric_difference(typer_params))

    def test_callback_interface_matches(self):
        from django_typer import callback

        callback_params = set(get_named_arguments(callback))
        typer_params = set(get_named_arguments(typer.Typer.callback))

        self.assertFalse(callback_params.symmetric_difference(typer_params))


class MultiTests(TestCase):
    def test_command_line(self):
        self.assertEqual(
            run_command("multi", "cmd1", "/path/one", "/path/two"),
            {"files": ["/path/one", "/path/two"], "flag1": False},
        )

        self.assertEqual(
            run_command("multi", "cmd1", "/path/four", "/path/three", "--flag1"),
            {"files": ["/path/four", "/path/three"], "flag1": True},
        )

        self.assertEqual(
            run_command("multi", "sum", "1.2", "3.5", " -12.3"), sum([1.2, 3.5, -12.3])
        )

        self.assertEqual(run_command("multi", "cmd3"), {})

    def test_call_command(self):
        ret = json.loads(call_command("multi", ["cmd1", "/path/one", "/path/two"]))
        self.assertEqual(ret, {"files": ["/path/one", "/path/two"], "flag1": False})

        ret = json.loads(
            call_command("multi", ["cmd1", "/path/four", "/path/three", "--flag1"])
        )
        self.assertEqual(ret, {"files": ["/path/four", "/path/three"], "flag1": True})

        ret = json.loads(call_command("multi", ["sum", "1.2", "3.5", " -12.3"]))
        self.assertEqual(ret, sum([1.2, 3.5, -12.3]))

        ret = json.loads(call_command("multi", ["cmd3"]))
        self.assertEqual(ret, {})

    def test_call_command_stdout(self):
        out = StringIO()
        call_command("multi", ["cmd1", "/path/one", "/path/two"], stdout=out)
        self.assertEqual(
            json.loads(out.getvalue()),
            {"files": ["/path/one", "/path/two"], "flag1": False},
        )

        out = StringIO()
        call_command(
            "multi", ["cmd1", "/path/four", "/path/three", "--flag1"], stdout=out
        )
        self.assertEqual(
            json.loads(out.getvalue()),
            {"files": ["/path/four", "/path/three"], "flag1": True},
        )

        out = StringIO()
        call_command("multi", ["sum", "1.2", "3.5", " -12.3"], stdout=out)
        self.assertEqual(json.loads(out.getvalue()), sum([1.2, 3.5, -12.3]))

        out = StringIO()
        call_command("multi", ["cmd3"], stdout=out)
        self.assertEqual(json.loads(out.getvalue()), {})

    def test_get_version(self):
        self.assertEqual(
            run_command("multi", "--version").strip(), django.get_version()
        )
        self.assertEqual(
            run_command("multi", "cmd1", "--version").strip(), django.get_version()
        )
        self.assertEqual(
            run_command("multi", "sum", "--version").strip(), django.get_version()
        )
        self.assertEqual(
            run_command("multi", "cmd3", "--version").strip(), django.get_version()
        )

    def test_call_direct(self):
        multi = load_command_class(get_commands()["multi"], "multi")

        self.assertEqual(
            json.loads(multi.cmd1(["/path/one", "/path/two"])),
            {"files": ["/path/one", "/path/two"], "flag1": False},
        )

        self.assertEqual(
            json.loads(multi.cmd1(["/path/four", "/path/three"], flag1=True)),
            {"files": ["/path/four", "/path/three"], "flag1": True},
        )

        self.assertEqual(float(multi.sum([1.2, 3.5, -12.3])), sum([1.2, 3.5, -12.3]))

        self.assertEqual(json.loads(multi.cmd3()), {})


class CallbackTests(TestCase):
    def test_command_line(self):
        self.assertEqual(
            run_command("callback1", "5", "callback1", "a1", "a2"),
            {
                "p1": 5,
                "flag1": False,
                "flag2": True,
                "arg1": "a1",
                "arg2": "a2",
                "arg3": 0.5,
                "arg4": 1,
            },
        )

        self.assertEqual(
            run_command(
                "callback1",
                "6",
                "--flag1",
                "--no-flag2",
                "callback1",
                "a1",
                "a2",
                "--arg3",
                "0.75",
                "--arg4",
                "2",
            ),
            {
                "p1": 6,
                "flag1": True,
                "flag2": False,
                "arg1": "a1",
                "arg2": "a2",
                "arg3": 0.75,
                "arg4": 2,
            },
        )

    def test_call_command(self):
        ret = json.loads(call_command("callback1", ["5", "callback1", "a1", "a2"]))
        self.assertEqual(
            ret,
            {
                "p1": 5,
                "flag1": False,
                "flag2": True,
                "arg1": "a1",
                "arg2": "a2",
                "arg3": 0.5,
                "arg4": 1,
            },
        )

        ret = json.loads(
            call_command(
                "callback1",
                [
                    "6",
                    "--flag1",
                    "--no-flag2",
                    "callback1",
                    "a1",
                    "a2",
                    "--arg3",
                    "0.75",
                    "--arg4",
                    "2",
                ],
            )
        )
        self.assertEqual(
            ret,
            {
                "p1": 6,
                "flag1": True,
                "flag2": False,
                "arg1": "a1",
                "arg2": "a2",
                "arg3": 0.75,
                "arg4": 2,
            },
        )

    # def test_call_command_stdout(self):
    #     out = StringIO()
    #     call_command('multi', ['cmd1', '/path/one', '/path/two'], stdout=out)
    #     self.assertEqual(json.loads(out.getvalue()), {'files': ['/path/one', '/path/two'], 'flag1': False})

    #     out = StringIO()
    #     call_command('multi', ['cmd1', '/path/four', '/path/three', '--flag1'], stdout=out)
    #     self.assertEqual(json.loads(out.getvalue()), {'files': ['/path/four', '/path/three'], 'flag1': True})

    #     out = StringIO()
    #     call_command('multi', ['sum', '1.2', '3.5', ' -12.3'], stdout=out)
    #     self.assertEqual(json.loads(out.getvalue()), sum([1.2, 3.5, -12.3]))

    #     out = StringIO()
    #     call_command('multi', ['cmd3'], stdout=out)
    #     self.assertEqual(json.loads(out.getvalue()), {})

    # def test_get_version(self):
    #     self.assertEqual(
    #         run_command('multi', '--version').strip(),
    #         django.get_version()
    #     )
    #     self.assertEqual(
    #         run_command('multi', 'cmd1', '--version').strip(),
    #         django.get_version()
    #     )
    #     self.assertEqual(
    #         run_command('multi', 'sum', '--version').strip(),
    #         django.get_version()
    #     )
    #     self.assertEqual(
    #         run_command('multi', 'cmd3', '--version').strip(),
    #         django.get_version()
    #     )

    # def test_call_direct(self):
    #     multi = load_command_class(get_commands()['multi'], 'multi')

    #     self.assertEqual(
    #         json.loads(multi.cmd1(['/path/one', '/path/two'])),
    #         {'files': ['/path/one', '/path/two'], 'flag1': False}
    #     )

    #     self.assertEqual(
    #         json.loads(multi.cmd1(['/path/four', '/path/three'], flag1=True)),
    #         {'files': ['/path/four', '/path/three'], 'flag1': True}
    #     )

    #     self.assertEqual(
    #         float(multi.sum([1.2, 3.5, -12.3])),
    #         sum([1.2, 3.5, -12.3])
    #     )

    #     self.assertEqual(
    #         json.loads(multi.cmd3()),
    #         {}
    #     )
