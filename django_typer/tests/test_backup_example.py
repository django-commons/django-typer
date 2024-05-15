import os

from django.test import SimpleTestCase
from pathlib import Path
from django_typer.tests.utils import run_command
import shutil


BACKUP_DIRECTORY = Path(__file__).parent / "_test_archive"


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
        lines = (
            run_command(
                "backup", "--no-color", "--settings", "django_typer.tests.settings.backup", "list"
            )[0]
            .strip()
            .splitlines()[1:]
        )
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0].strip(),
            "database(filename={database}.json, databases=['default'])",
        )

        self.assertEqual(
            run_command(
                "backup",
                "--settings",
                "django_typer.tests.settings.backup",
                "-o",
                str(BACKUP_DIRECTORY),
            )[-1],
            0,
        )

        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 1)

    def test_inherit_backup(self):
        lines = [
            line.strip()
            for line in run_command(
                "backup",
                "--no-color",
                "--settings",
                "django_typer.tests.settings.backup_inherit",
                "list",
            )[0]
            .strip()
            .splitlines()[1:]
        ]
        self.assertEqual(len(lines), 2)
        self.assertTrue(
            "database(filename={database}.json, databases=['default'])" in lines
        )
        self.assertTrue("media(filename=media.tar.gz)" in lines)

        self.assertEqual(
            run_command(
                "backup",
                "--settings",
                "django_typer.tests.settings.backup_inherit",
                "-o",
                str(BACKUP_DIRECTORY),
            )[-1],
            0,
        )

        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 2)

    def test_extend_backup(self):
        lines = [
            line.strip()
            for line in run_command(
                "backup", "--no-color", "--settings", "django_typer.tests.settings.backup_ext", "list"
            )[0]
            .strip()
            .splitlines()[1:]
        ]
        self.assertEqual(len(lines), 3)
        self.assertTrue(
            "database(filename={database}.json, databases=['default'])" in lines
        )
        self.assertTrue("environment(filename=requirements.txt)" in lines)
        self.assertTrue("media(filename=media.tar.gz)" in lines)

        self.assertEqual(
            run_command(
                "backup",
                "--settings",
                "django_typer.tests.settings.backup_ext",
                "-o",
                str(BACKUP_DIRECTORY),
            )[-1],
            0,
        )

        self.assertTrue(BACKUP_DIRECTORY.exists())
        self.assertTrue((BACKUP_DIRECTORY / "default.json").exists())
        self.assertTrue((BACKUP_DIRECTORY / "media.tar.gz").exists())
        self.assertTrue((BACKUP_DIRECTORY / "requirements.txt").exists())
        self.assertTrue(len(os.listdir(BACKUP_DIRECTORY)) == 3)
