from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class TestStatic(TestCase):
    cmd = "static"

    def test_run(self):
        stdout, stderr, retcode = run_command(self.cmd)
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "init")

        stdout, stderr, retcode = run_command(self.cmd, "cmd1")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "cmd1")

        stdout, stderr, retcode = run_command(self.cmd, "cmd2")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "cmd2")

        stdout, stderr, retcode = run_command(self.cmd, "grp1")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp1")

        stdout, stderr, retcode = run_command(self.cmd, "grp2")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp2")

        stdout, stderr, retcode = run_command(self.cmd, "grp1", "grp1-cmd")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp1_cmd")

        stdout, stderr, retcode = run_command(self.cmd, "grp2", "grp2-cmd")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp2_cmd")

        stdout, stderr, retcode = run_command(self.cmd, "grp2", "grp2-subgrp")
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp2_subgrp")

        stdout, stderr, retcode = run_command(
            self.cmd, "grp2", "grp2-subgrp", "grp2-subgrp-cmd"
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), "grp2_subgrp_cmd")

    def test_call(self):
        stdout = call_command(self.cmd)
        self.assertEqual(stdout.strip(), "init")

        stdout = call_command(self.cmd, "cmd1")
        self.assertEqual(stdout.strip(), "cmd1")

        stdout = call_command(self.cmd, "cmd2")
        self.assertEqual(stdout.strip(), "cmd2")

        stdout = call_command(self.cmd, "grp1")
        self.assertEqual(stdout.strip(), "grp1")

        stdout = call_command(self.cmd, "grp2")
        self.assertEqual(stdout.strip(), "grp2")

        stdout = call_command(self.cmd, "grp1", "grp1-cmd")
        self.assertEqual(stdout.strip(), "grp1_cmd")

        stdout = call_command(self.cmd, "grp2", "grp2-cmd")
        self.assertEqual(stdout.strip(), "grp2_cmd")

        stdout = call_command(self.cmd, "grp2", "grp2-subgrp")
        self.assertEqual(stdout.strip(), "grp2_subgrp")

        stdout = call_command(self.cmd, "grp2", "grp2-subgrp", "grp2-subgrp-cmd")
        self.assertEqual(stdout.strip(), "grp2_subgrp_cmd")

    def test_direct(self):
        from tests.apps.test_app.management.commands.static import (
            Command as Static,
        )

        static = get_command(self.cmd, Static)

        self.assertEqual(static.init(), "init")
        self.assertEqual(static.cmd1(), "cmd1")
        self.assertEqual(static.cmd2(), "cmd2")
        self.assertEqual(static.grp1(), "grp1")
        self.assertEqual(static.grp2(), "grp2")
        self.assertEqual(static.grp1_cmd(), "grp1_cmd")
        self.assertEqual(static.grp2_cmd(), "grp2_cmd")

        self.assertEqual(static.grp2_subgrp(), "grp2_subgrp")
        self.assertEqual(static.grp2_subgrp_cmd(), "grp2_subgrp_cmd")

        self.assertEqual(static.grp2.grp2_subgrp(), "grp2_subgrp")
        self.assertEqual(static.grp2.grp2_subgrp.grp2_subgrp_cmd(), "grp2_subgrp_cmd")


class TestStatic2(TestStatic):
    cmd = "static2"
