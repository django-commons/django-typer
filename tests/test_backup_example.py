import datetime
import os
import shutil
from pathlib import Path

import pytest
from django.test import TestCase
from django.db import connection

from tests.utils import run_command

BACKUP_DIRECTORY = Path(__file__).parent / "_test_archive"


class TestBackupExample(TestCase):
    databases = {"default"}

    typer = ""

    @classmethod
    def setUpClass(cls) -> None:
        if connection.vendor != "sqlite":
            run_command("migrate")
        super().setUpClass()

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
            f"backup{self.typer}",
            "--no-color",
            "--settings",
            "tests.settings.backup",
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
            f"backup{self.typer}",
            "--settings",
            "tests.settings.backup",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 1)

    def test_inherit_backup(self):
        stdout, stderr, retcode = run_command(
            f"backup{self.typer}",
            "--no-color",
            "--settings",
            "tests.settings.backup_inherit",
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
            f"backup{self.typer}",
            "--settings",
            "tests.settings.backup_inherit",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 2)

    @pytest.mark.skipif(
        connection.vendor != "sqlite",
        reason="Skipped because the database should be sqlite",
    )
    def test_extend_backup(self):
        stdout, stderr, retcode = run_command(
            f"backup{self.typer}",
            "--no-color",
            "--settings",
            "tests.settings.backup_ext",
            "list",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        lines = [line.strip() for line in stdout.strip().splitlines()[1:]]
        self.assertEqual(len(lines), 3)
        self.assertTrue("database()" in lines)
        self.assertTrue("environment(filename=requirements.txt)" in lines)
        self.assertTrue("media(filename=media.tar.gz)" in lines)

        stdout, stderr, retcode = run_command(
            f"backup{self.typer}",
            "--settings",
            "tests.settings.backup_ext",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue(
            (BACKUP_DIRECTORY / f"backup_{datetime.date.today()}.sqlite3").exists()
        )
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue((BACKUP_DIRECTORY / "requirements.txt").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 3)

    def test_backup_pluggy(self):
        stdout, stderr, retcode = run_command(
            f"backup{self.typer}",
            "--no-color",
            "--settings",
            "tests.settings.backup_pluggy",
            "list",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        lines = [line.strip() for line in stdout.strip().splitlines()[1:]]
        self.assertEqual(len(lines), 3)
        self.assertTrue(
            "database(filename={database}.json, databases=['default'])" in lines
        )
        self.assertTrue("media(filename=media.tar.gz)" in lines)
        self.assertTrue("files()" in lines)

        stdout, stderr, retcode = run_command(
            f"backup{self.typer}",
            "--settings",
            "tests.settings.backup_pluggy",
            "-o",
            str(BACKUP_DIRECTORY),
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 2)

        self.assertTrue("files1.tar.gz" in stdout)
        self.assertTrue("files2.zip" in stdout)


class TestBackupTyperExample(TestBackupExample):
    typer = "_typer"
