import os
import shutil
import sys
from pathlib import Path

import pytest
import platform
from django.test import TestCase
from django_typer.management.commands.shells.powershell import PowerShellComplete

from tests.shellcompletion import (
    _DefaultCompleteTestCase,
    _InstalledScriptTestCase,
)


@pytest.mark.skipif(
    shutil.which("powershell") is None, reason="Powershell not available"
)
class PowerShellTests(_DefaultCompleteTestCase, TestCase):
    shell = "powershell"
    profile: Path

    environment = [
        f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8{os.linesep}",
        f"$env:DJANGO_SETTINGS_MODULE='tests.settings.completion'{os.linesep}",
        f"{Path(sys.executable).absolute().parent / 'activate.ps1'}{os.linesep}",
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = PowerShellComplete().get_user_profile()
        return super().setUpClass()

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue(self.profile.exists())
        self.assertTrue(
            f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
            in self.profile.read_text()
        )

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        if self.profile.exists():
            contents = self.profile.read_text()
            self.assertFalse(
                f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
                in contents
            )
            self.assertTrue(contents)  # should have been deleted if it were empty


@pytest.mark.skipif(
    shutil.which("powershell") is None, reason="Powershell not available"
)
class PowerShellExeTests(_InstalledScriptTestCase, PowerShellTests):
    pass
