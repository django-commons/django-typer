import shutil
import sys
from pathlib import Path
import platform
import typing as t

import pytest
from django.core.management import CommandError
from django.test import TestCase
from django_typer.shells.powershell import (
    PowerShellComplete,
    PwshComplete,
)

from tests.shellcompletion import (
    _ScriptCompleteTestCase,
    _InstalledScriptCompleteTestCase,
)


class _PowerShellMixin:
    shell = "powershell"
    profile: Path
    tabs = "\t"
    completer_class = PowerShellComplete

    environment = [
        f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
        f"$env:DJANGO_SETTINGS_MODULE='tests.settings.completion'",
        f'$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"',
        f"{Path(sys.executable).absolute().parent / 'activate.ps1'}",
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = cls.completer_class().get_user_profile()
        return super().setUpClass()

    def verify_install(self, script=None, directory: t.Optional[Path] = None):
        if not script:
            script = self.manage_script
        self.assertTrue(self.profile.exists())
        self.assertTrue(
            f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
            in self.profile.read_text()
        )

    def verify_remove(self, script=None, directory: t.Optional[Path] = None):
        if not script:
            script = self.manage_script
        if self.profile.exists():
            contents = self.profile.read_text()
            self.assertFalse(
                f"Register-ArgumentCompleter -Native -CommandName {script} -ScriptBlock $scriptblock"
                in contents
            )
            self.assertTrue(contents)  # should have been deleted if it were empty

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only test")
    def test_mixed_path_dividers(self):
        self.install()
        self.verify_install()
        completions = self.get_completions(
            "completion", "--path", "./src/django_typer\\comp"
        )
        self.assertIn(
            "src\\django_typer\\completers",
            completions,
        )
        self.remove()
        self.verify_remove()


@pytest.mark.skipif(
    shutil.which("powershell") is None, reason="powershell not available"
)
class PowerShellTests(_PowerShellMixin, _ScriptCompleteTestCase, TestCase):
    def test_shell_complete(self):
        with self.assertRaises(CommandError):
            self.install()

    @pytest.mark.rich
    @pytest.mark.no_rich
    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_rich_output(self): ...

    @pytest.mark.rich
    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_no_rich_output(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_settings_pass_through(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_pythonpath_pass_through(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_fallback(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_reentrant_install_uninstall(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_path_completion(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_mixed_path_dividers(self): ...


@pytest.mark.skipif(
    shutil.which("powershell") is None, reason="Powershell not available"
)
class PowerShellExeTests(_PowerShellMixin, _InstalledScriptCompleteTestCase, TestCase):
    pass


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not available")
class PWSHTests(_PowerShellMixin, _ScriptCompleteTestCase, TestCase):
    shell = "pwsh"
    completer_class = PwshComplete

    def test_shell_complete(self):
        with self.assertRaises(CommandError):
            self.install()

    @pytest.mark.rich
    @pytest.mark.no_rich
    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_rich_output(self): ...

    @pytest.mark.rich
    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_no_rich_output(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_settings_pass_through(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_pythonpath_pass_through(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_fallback(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_reentrant_install_uninstall(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_path_completion(self): ...

    @pytest.mark.skip(reason="powershell does not support script installations")
    def test_mixed_path_dividers(self): ...


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not available")
class PWSHExeTests(_PowerShellMixin, _InstalledScriptCompleteTestCase, TestCase):
    shell = "pwsh"
    completer_class = PwshComplete

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only test")
    def test_mixed_path_dividers(self):
        self.install()
        self.verify_install()
        self.assertIn(
            "src\\django_typer\\completers",
            self.get_completions("completion", "--path", "./src/django_typer\\comp"),
        )
        self.remove()
        self.verify_remove()
