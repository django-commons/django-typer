from django.core.management import call_command
from django.test import TestCase

from django_typer.management import TyperCommand, get_command
from tests.utils import run_command


class TestHandle(TestCase):
    cmd = "handle"

    def test_handle_run(self):
        stdout, stderr, retcode = run_command(self.cmd)
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), self.cmd)

    def test_handle_call(self):
        self.assertEqual(call_command(self.cmd).strip(), self.cmd)

    def test_handle_direct(self):
        self.assertEqual(get_command(self.cmd, TyperCommand)(), self.cmd)


class TestHandleInheritOverrideAsCommand(TestHandle):
    cmd = "handle1"


class TestHandleAsCommand(TestHandle):
    cmd = "handle2"


class TestHandleOverride(TestHandle):
    cmd = "handle3"


class TestHandleAsCommandOverride(TestHandle):
    cmd = "handle4"


class TestNoHandle(TestCase):
    cmd = "handle_none"

    def test_no_handle_run(self):
        stdout, stderr, retcode = run_command(self.cmd)
        self.assertGreater(retcode, 0, msg=stderr)
        self.assertTrue("NotImplementedError" in stderr.strip())

    def test_no_handle_call(self):
        with self.assertRaises(NotImplementedError):
            call_command(self.cmd)

    def test_no_handle_direct(self):
        with self.assertRaises(NotImplementedError):
            get_command(self.cmd, TyperCommand)()
