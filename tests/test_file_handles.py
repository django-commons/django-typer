import contextlib
from io import StringIO
from pathlib import Path
from django.core.management import call_command
from django.test import TestCase
from django_typer.management.commands.shellcompletion import Command as ShellCompletion
from django_typer.management import get_command
from tests.utils import run_command

file_text = Path(__file__).parent / "media/file_text.txt"
file_text_write = Path(__file__).parent / "media/file_text_write.txt"
file_binary = Path(__file__).parent / "media/file_binary.txt"
file_binary_write = Path(__file__).parent / "media/file_binary_write.txt"


class TestFileHandles(TestCase):
    def test_file_handles_shell_complete(self):
        shellcompletion = get_command("shellcompletion", ShellCompletion)
        self.assertTrue(
            file_text.name
            in shellcompletion.complete(f"file_handles {file_text.parent}")
        )

    def test_file_handles_run(self):
        try:
            self.assertTrue(file_text.exists())
            self.assertTrue(file_binary.exists())
            stdout, stderr, retcode = run_command(
                "file_handles",
                file_text,
                file_text_write,
                file_binary,
                file_binary_write,
            )
            self.assertEqual(retcode, 0, stderr)
        finally:
            # Clean up the files created during the test
            if file_text_write.exists():
                file_text_write.unlink()
            if file_binary_write.exists():
                file_binary_write.unlink()

    def test_file_handles_run_pipe(self):
        try:
            self.assertTrue(file_text.exists())
            self.assertTrue(file_binary.exists())
            with open(file_text, "r", encoding="utf-8") as f:
                _, stderr, retcode = run_command(
                    "file_handles",
                    "-",
                    file_text_write,
                    file_binary,
                    file_binary_write,
                    stdin=f,
                )
            self.assertEqual(retcode, 0, stderr)
        finally:
            # Clean up the files created during the test
            if file_text_write.exists():
                file_text_write.unlink()
            if file_binary_write.exists():
                file_binary_write.unlink()

    def test_file_handles_call(self):
        try:
            self.assertTrue(file_text.exists())
            self.assertTrue(file_binary.exists())
            call_command(
                "file_handles",
                str(file_text),
                str(file_text_write),
                str(file_binary),
                str(file_binary_write),
            )
        finally:
            # Clean up the files created during the test
            if file_text_write.exists():
                file_text_write.unlink()
            if file_binary_write.exists():
                file_binary_write.unlink()

    def test_file_handles_direct(self):
        from tests.apps.test_app.management.commands.file_handles import (
            Command as FileHandles,
        )

        try:
            self.assertTrue(file_text.exists())
            self.assertTrue(file_binary.exists())
            file_handles = get_command("file_handles", FileHandles)
            file_handles(
                file_text=file_text.open("r", encoding="utf-8"),
                file_text_write=file_text_write.open("w", encoding="utf-8"),
                file_binary=file_binary.open("rb"),
                file_binary_write=file_binary_write.open("wb"),
            )
        finally:
            # Clean up the files created during the test
            if file_text_write.exists():
                file_text_write.unlink()
            if file_binary_write.exists():
                file_binary_write.unlink()
