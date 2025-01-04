import shutil
from pathlib import Path

import pytest
from django.test import TestCase
import os
import sys

from tests.shellcompletion import _DefaultCompleteTestCase, _InstalledScriptTestCase


@pytest.mark.skipif(shutil.which("zsh") is None, reason="Z-Shell not available")
class ZshTests(_DefaultCompleteTestCase, TestCase):
    shell = "zsh"
    directory = Path("~/.zfunc").expanduser()
    interactive_opt = "-i"

    environment = [
        f"PATH={Path(sys.executable).parent}:$PATH{os.linesep}"
        f"DJANGO_SETTINGS_MODULE=tests.settings.completion{os.linesep}"
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
class ZshExeTests(_InstalledScriptTestCase, ZshTests, TestCase):
    shell = "zsh"
