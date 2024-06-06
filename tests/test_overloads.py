import json

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestOverloaded(TestCase):
    """
    Tests that overloaded group/command names work as expected.
    """

    def test_overloaded_direct(self):
        overloaded = get_command("overloaded")
        overloaded.test(1, flag=True)
        self.assertEqual(
            json.loads(overloaded.samename(5, flag=False)),
            {
                "samename": {"precision": 5, "flag": False},
                "test": {"precision": 1, "flag": True},
            },
        )

        overloaded.test(5, flag=False)
        self.assertEqual(
            json.loads(overloaded.samename(1, flag=True)),
            {
                "samename": {"precision": 1, "flag": True},
                "test": {"precision": 5, "flag": False},
            },
        )

        overloaded.test(1, flag=True)
        self.assertEqual(
            json.loads(overloaded.diffname(5, flag2=False)),
            {
                "diffname": {"precision2": 5, "flag2": False},
                "test": {"precision": 1, "flag": True},
            },
        )

        overloaded.test(5, flag=False)
        self.assertEqual(
            json.loads(overloaded.diffname(1, flag2=True)),
            {
                "diffname": {"precision2": 1, "flag2": True},
                "test": {"precision": 5, "flag": False},
            },
        )

    def test_overloaded_cli(self):
        result = run_command(
            "overloaded", "test", "--flag", "1", "samename", "5", "--no-flag"
        )[0]
        self.assertEqual(
            result,
            {
                "samename": {"precision": 5, "flag": False},
                "test": {"precision": 1, "flag": True},
            },
        )

        result = run_command(
            "overloaded", "test", "--no-flag", "5", "samename", "1", "--flag"
        )[0]
        self.assertEqual(
            result,
            {
                "samename": {"precision": 1, "flag": True},
                "test": {"precision": 5, "flag": False},
            },
        )
        result = run_command(
            "overloaded", "test", "--flag", "1", "diffname", "5", "--no-flag"
        )[0]
        self.assertEqual(
            result,
            {
                "diffname": {"precision2": 5, "flag2": False},
                "test": {"precision": 1, "flag": True},
            },
        )

        result = run_command(
            "overloaded", "test", "--no-flag", "5", "diffname", "1", "--flag"
        )[0]
        self.assertEqual(
            result,
            {
                "diffname": {"precision2": 1, "flag2": True},
                "test": {"precision": 5, "flag": False},
            },
        )

    def test_overloaded_call_command(self):
        self.assertEqual(
            json.loads(
                call_command(
                    "overloaded",
                    ["test", "--flag", "1", "samename", "5", "--no-flag"],
                )
            ),
            {
                "samename": {"precision": 5, "flag": False},
                "test": {"precision": 1, "flag": True},
            },
        )
        self.assertEqual(
            json.loads(
                call_command(
                    "overloaded",
                    ["test", "--no-flag", "5", "samename", "1", "--flag"],
                )
            ),
            {
                "test": {"precision": 5, "flag": False},
                "samename": {"precision": 1, "flag": True},
            },
        )

        ret = json.loads(
            call_command("overloaded", ["test", "5", "samename", "1"], flag=True)
        )
        self.assertEqual(
            ret,
            {
                "test": {"precision": 5, "flag": True},
                "samename": {"precision": 1, "flag": True},
            },
        )

        self.assertEqual(
            json.loads(
                call_command(
                    "overloaded",
                    ["test", "--no-flag", "5", "diffname", "1", "--flag"],
                )
            ),
            {
                "diffname": {"precision2": 1, "flag2": True},
                "test": {"precision": 5, "flag": False},
            },
        )
        self.assertEqual(
            json.loads(
                call_command(
                    "overloaded",
                    ["test", "--flag", "1", "diffname", "5", "--no-flag"],
                )
            ),
            {
                "diffname": {"precision2": 5, "flag2": False},
                "test": {"precision": 1, "flag": True},
            },
        )
        self.assertEqual(
            json.loads(
                call_command(
                    "overloaded", ["test", "5", "diffname", "1"], flag=True, flag2=False
                )
            ),
            {
                "diffname": {"precision2": 1, "flag2": False},
                "test": {"precision": 5, "flag": True},
            },
        )


class TestGroupOverloads(TestCase):
    def test_grp_overload_run(self):
        stdout, stderr, retcode = run_command("grp_overload", "g0", "l2", "1")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g0:l2(1)")

        stdout, stderr, retcode = run_command("grp_overload", "g1", "l2", "a")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g1:l2(a)")

        stdout, stderr, retcode = run_command("grp_overload", "g0", "l2", "1", "cmd")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g0:l2:cmd()")

        stdout, stderr, retcode = run_command("grp_overload", "g1", "l2", "a", "cmd")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g1:l2:cmd()")

        stdout, stderr, retcode = run_command("grp_overload", "g0", "l2", "1", "cmd2")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g0:l2:cmd2()")

        stdout, stderr, retcode = run_command("grp_overload", "g1", "l2", "a", "cmd2")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "g1:l2:cmd2()")

    def test_grp_overload_call(self):
        stdout = call_command("grp_overload", "g0", "l2", "1")
        self.assertEqual(stdout.strip(), "g0:l2(1)")

        stdout = call_command("grp_overload", "g1", "l2", "a")
        self.assertEqual(stdout.strip(), "g1:l2(a)")

        stdout = call_command("grp_overload", "g0", "l2", "1", "cmd")
        self.assertEqual(stdout.strip(), "g0:l2:cmd()")

        stdout = call_command("grp_overload", "g1", "l2", "a", "cmd")
        self.assertEqual(stdout.strip(), "g1:l2:cmd()")

        stdout = call_command("grp_overload", "g0", "l2", "1", "cmd2")
        self.assertEqual(stdout.strip(), "g0:l2:cmd2()")

        stdout = call_command("grp_overload", "g1", "l2", "a", "cmd2")
        self.assertEqual(stdout.strip(), "g1:l2:cmd2()")

    def test_grp_overload_direct(self):
        from tests.apps.test_app.management.commands.grp_overload import (
            Command as GrpOverload,
        )

        grp_overload = get_command("grp_overload", GrpOverload)

        print("----------")
        self.assertEqual(grp_overload.g1.l2("a"), "g1:l2(a)")
        print("----------")
        self.assertEqual(grp_overload.g0.l2(1), "g0:l2(1)")
        print("----------")
        self.assertEqual(grp_overload.g0.l2.cmd(), "g0:l2:cmd()")
        print("----------")
        self.assertEqual(grp_overload.g1.l2.cmd(), "g1:l2:cmd()")
        print("----------")

        self.assertTrue(hasattr(grp_overload.g0.l2, "cmd2"))
        self.assertEqual(grp_overload.g0.l2.cmd2(), "g0:l2:cmd2()")
        self.assertEqual(grp_overload.g1.l2.cmd2(), "g1:l2:cmd2()")
