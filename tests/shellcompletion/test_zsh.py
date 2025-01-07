import shutil
from pathlib import Path

import pytest
from django.test import TestCase
import sys
import os

from tests.shellcompletion import (
    _ScriptCompleteTestCase,
    _InstalledScriptCompleteTestCase,
)


@pytest.mark.skipif(shutil.which("zsh") is None, reason="Z-Shell not available")
class ZshTests(_ScriptCompleteTestCase, TestCase):
    shell = "zsh"
    directory = Path("~/.zfunc").expanduser()
    interactive_opt = "-i"
    tabs = "\t\t\t"

    environment = [
        f"PATH={Path(sys.executable).parent}:$PATH",
        f"DJANGO_SETTINGS_MODULE=tests.settings.completion",
    ]

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / f"_{script}").exists())

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        self.assertFalse((self.directory / f"_{script}").exists())


@pytest.mark.skipif(shutil.which("zsh") is None, reason="Z-Shell not available")
class ZshExeTests(_InstalledScriptCompleteTestCase, ZshTests, TestCase):
    shell = "zsh"

    @pytest.mark.skipif(
        not bool(os.environ.get("ENABLE_CI_ONLY_TESTS", False)),
        reason="This test is dangerous to run on a user machine, "
        "because it may nuke their shell profile file.",
    )
    def test_no_zshrc_file(self):
        zshrc = ""
        try:
            if (Path.home() / ".zshrc").exists():
                zshrc = (Path.home() / ".zshrc").read_text()
                os.unlink(Path.home() / ".zshrc")
            self.test_shell_complete()
        finally:
            if zshrc:
                (Path.home() / ".zshrc").write_text(zshrc)
