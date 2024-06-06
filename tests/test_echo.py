from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command


class EchoWrapperTests(TestCase):
    def test_echo_no_color(self):
        result = run_command(
            "echo", "--no-color", "echo-test", "Brian Kohan", "--color", "magenta"
        )[0]
        self.assertTrue("\x1b[35m" not in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        result = run_command(
            "echo",
            "--no-color",
            "echo-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            "--no-nl",
        )[1]
        self.assertTrue("\x1b[35m" not in result)
        self.assertTrue("\n" not in result)
        self.assertTrue("Brian Kohan" in result)

    def test_echo_force_color(self):
        result = run_command(
            "echo", "--force-color", "echo-test", "Brian Kohan", "--color", "magenta"
        )[0]
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        result = run_command(
            "echo",
            "--force-color",
            "echo-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            "--no-nl",
        )[1]
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" not in result)
        self.assertTrue("Brian Kohan" in result)

    def test_echo_call_command(self):
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        call_command(
            "echo",
            "--force-color",
            "echo-test",
            "Brian Kohan",
            "--color",
            "magenta",
            stdout=stdout_buffer,
            stderr=stderr_buffer,
        )
        result = stdout_buffer.getvalue()
        stdout_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        call_command(
            "echo",
            "--force-color",
            "echo-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            stdout=stdout_buffer,
            stderr=stderr_buffer,
        )
        result = stderr_buffer.getvalue()
        stderr_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

    def test_echo_get_command(self):
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        echo = get_command(
            "echo", force_color=True, stdout=stdout_buffer, stderr=stderr_buffer
        )
        echo.echo_test("Brian Kohan", color="magenta")
        result = stdout_buffer.getvalue()
        stdout_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        echo.echo_test("Brian Kohan", color="magenta", error=True)
        result = stderr_buffer.getvalue()
        stderr_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

    def test_secho_no_color(self):
        result = run_command(
            "echo", "--no-color", "secho-test", "Brian Kohan", "--color", "magenta"
        )[0]
        self.assertTrue("\x1b[35m" not in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        result = run_command(
            "echo",
            "--no-color",
            "secho-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            "--no-nl",
        )[1]
        self.assertTrue("\x1b[35m" not in result)
        self.assertTrue("\n" not in result)
        self.assertTrue("Brian Kohan" in result)

    def test_secho_force_color(self):
        result = run_command(
            "echo", "--force-color", "secho-test", "Brian Kohan", "--color", "magenta"
        )[0]
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        result = run_command(
            "echo",
            "--force-color",
            "secho-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            "--no-nl",
        )[1]
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" not in result)
        self.assertTrue("Brian Kohan" in result)

    def test_secho_call_command(self):
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        call_command(
            "echo",
            "--force-color",
            "secho-test",
            "Brian Kohan",
            "--color",
            "magenta",
            stdout=stdout_buffer,
            stderr=stderr_buffer,
        )
        result = stdout_buffer.getvalue()
        stdout_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        call_command(
            "echo",
            "--force-color",
            "secho-test",
            "Brian Kohan",
            "--color",
            "magenta",
            "--error",
            stdout=stdout_buffer,
            stderr=stderr_buffer,
        )
        result = stderr_buffer.getvalue()
        stderr_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

    def test_secho_get_command(self):
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        echo = get_command(
            "echo", force_color=True, stdout=stdout_buffer, stderr=stderr_buffer
        )
        echo.secho_test("Brian Kohan", color="magenta")
        result = stdout_buffer.getvalue()
        stdout_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)

        echo.secho_test("Brian Kohan", color="magenta", error=True)
        result = stderr_buffer.getvalue()
        stderr_buffer.seek(0)
        self.assertTrue("\x1b[35m" in result)
        self.assertTrue("\n" in result)
        self.assertTrue("Brian Kohan" in result)
