import os
import shutil
import sys
from pathlib import Path

import pytest
from django.test import TestCase

from tests.shellcompletion import _DefaultCompleteTestCase, _InstalledScriptTestCase


@pytest.mark.skipif(shutil.which("bash") is None, reason="Bash not available")
class BashTests(_DefaultCompleteTestCase, TestCase):
    shell = "bash"
    directory = Path("~/.bash_completions").expanduser()
    interactive_opt = "-i"

    environment = [
        f"export DJANGO_SETTINGS_MODULE=tests.settings.completion{os.linesep}",
        f"source ~/.bashrc{os.linesep}",
        f"source {Path(sys.executable).absolute().parent / 'activate'}{os.linesep}",
    ]

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / f"{script}.sh").exists())

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        self.assertFalse((self.directory / f"{script}.sh").exists())

    @pytest.mark.rich
    @pytest.mark.no_rich
    @pytest.mark.skip("Bash completer does not support rich output.")
    def test_rich_output(self): ...


@pytest.mark.skipif(shutil.which("bash") is None, reason="Bash not available")
class BashExeTests(_InstalledScriptTestCase, BashTests):
    shell = "bash"
