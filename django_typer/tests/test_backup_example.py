import os
import sys
import pytest

from django.test import SimpleTestCase
from pathlib import Path
from django_typer.tests.utils import run_command
import shutil


BACKUP_DIRECTORY = Path(__file__).parent / "_test_archive"


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
class TestBackupExample(SimpleTestCase):
    databases = {"default"}

    def setUp(self):
        if BACKUP_DIRECTORY.exists():
            shutil.rmtree(BACKUP_DIRECTORY)
        super().setUp()

    def tearDown(self) -> None:
        if BACKUP_DIRECTORY.exists():
            shutil.rmtree(BACKUP_DIRECTORY)
        return super().tearDown()

    def test_base_backup(self):
        stdout, stderr, retcode = run_command(
            "backup",
            "--no-color",
            "--settings",
            "django_typer.tests.settings.backup",
            "list",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        lines = stdout.strip().splitlines()[1:]
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0].strip(),
            "database(filename={database}.json, databases=['default'])",
        )

        stdout, stderr, retcode = run_command(
            "backup",
            "--settings",
            "django_typer.tests.settings.backup",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 1)

    def test_inherit_backup(self):
        stdout, stderr, retcode = run_command(
            "backup",
            "--no-color",
            "--settings",
            "django_typer.tests.settings.backup_inherit",
            "list",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        lines = [line.strip() for line in stdout.strip().splitlines()[1:]]
        self.assertEqual(len(lines), 2)
        self.assertTrue(
            "database(filename={database}.json, databases=['default'])" in lines
        )
        self.assertTrue("media(filename=media.tar.gz)" in lines)

        stdout, stderr, retcode = run_command(
            "backup",
            "--settings",
            "django_typer.tests.settings.backup_inherit",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 2)

    def test_extend_backup(self):
        stdout, stderr, retcode = run_command(
            "backup",
            "--no-color",
            "--settings",
            "django_typer.tests.settings.backup_ext",
            "list",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        lines = [line.strip() for line in stdout.strip().splitlines()[1:]]
        self.assertEqual(len(lines), 3)
        self.assertTrue(
            "database(filename={database}.json, databases=['default'])" in lines
        )
        self.assertTrue("environment(filename=requirements.txt)" in lines)
        self.assertTrue("media(filename=media.tar.gz)" in lines)

        stdout, stderr, retcode = run_command(
            "backup",
            "--settings",
            "django_typer.tests.settings.backup_ext",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue((BACKUP_DIRECTORY / "requirements.txt").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 3)
