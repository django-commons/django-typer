import shutil
import sys
from pathlib import Path

import pytest
from django.test import TestCase
from django.core.management import CommandError

from tests.shellcompletion import (
    _ScriptCompleteTestCase,
    _InstalledScriptCompleteTestCase,
)


class _FishMixin:
    shell = "fish"
    profile: Path
    tabs = "\t\t"
    directory = Path("~/.config/fish/completions").expanduser()

    environment = [
        f"set -x DJANGO_SETTINGS_MODULE 'tests.settings.completion'"
        f"{Path(sys.executable).absolute().parent / 'activate.fish'}",
    ]

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / f"{script}.fish").exists())

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        self.assertFalse((self.directory / f"{script}.fish").exists())


@pytest.mark.skipif(shutil.which("fish") is None, reason="Fish not available")
class FishShellTests(_FishMixin, _ScriptCompleteTestCase, TestCase):
    def test_shell_complete(self):
        with self.assertRaises(CommandError):
            self.install()

    @pytest.mark.rich
    @pytest.mark.no_rich
    @pytest.mark.skip(reason="fish does not support script installations")
    def test_rich_output(self): ...

    @pytest.mark.rich
    @pytest.mark.skip(reason="fish does not support script installations")
    def test_no_rich_output(self): ...

    @pytest.mark.skip(reason="fish does not support script installations")
    def test_settings_pass_through(self): ...

    @pytest.mark.skip(reason="fish does not support script installations")
    def test_pythonpath_pass_through(self): ...


@pytest.mark.skipif(shutil.which("fish") is None, reason="Fish not available")
class FishExeShellTests(_FishMixin, _InstalledScriptCompleteTestCase, TestCase):
    pass
