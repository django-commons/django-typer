import pytest
import shutil
from django_typer.tests.shellcompletion import (
    _DefaultCompleteTestCase,
    _InstalledScriptTestCase,
)
from django.test import TestCase
import os
import sys
from pathlib import Path


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="Powershell not available")
class PowerShellTests(_DefaultCompleteTestCase, TestCase):
    shell = "pwsh"
    directory = Path("~/.config/powershell").expanduser()

    @property
    def interactive_opt(self):
        return "-i"

    def set_environment(self, fd):
        os.write(
            fd, "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n".encode()
        )
        os.write(fd, f"PATH={Path(sys.executable).parent}:$env:PATH\n".encode())
        os.write(
            fd,
            f'$env:DJANGO_SETTINGS_MODULE="{os.environ["DJANGO_SETTINGS_MODULE"]}"\n'.encode(),
        )

    def test_shell_complete(self):
        # just verify that install/remove works. The actual completion is not tested
        # because there's an issue getting non garbled output back from the pty that
        # works for the other tests
        # TODO - fix this
        self.install()
        self.remove()

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / "Microsoft.PowerShell_profile.ps1").exists())
        self.assertTrue(
            f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
            in (self.directory / "Microsoft.PowerShell_profile.ps1").read_text()
        )

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        if (self.directory / "Microsoft.PowerShell_profile.ps1").exists():
            contents = (self.directory / "Microsoft.PowerShell_profile.ps1").read_text()
            self.assertFalse(
                f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
                in contents
            )
            self.assertTrue(contents)  # should have been deleted if it were empty


class PowerShellInstallRemoveTests(_InstalledScriptTestCase, PowerShellTests):
    def test_shell_complete(self):
        # the power shell completion script registration is all in one file
        # so install/remove is more complicated when other scripts are in that
        # file - this tests that
        self.install(script="./manage.py")
        self.verify_install(script="./manage.py")
        self.install(script=self.manage_script)
        self.verify_install(script=self.manage_script)
        self.remove(script=self.manage_script)
        self.verify_remove(script=self.manage_script)
        self.remove(script="./manage.py")
        self.verify_remove(script="./manage.py")
