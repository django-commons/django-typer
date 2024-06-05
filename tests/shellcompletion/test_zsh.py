import shutil
from pathlib import Path

import pytest
from django.test import TestCase

from tests.shellcompletion import _DefaultCompleteTestCase


@pytest.mark.skipif(shutil.which("zsh") is None, reason="Z-Shell not available")
class ZshShellTests(_DefaultCompleteTestCase, TestCase):
    shell = "zsh"
    directory = Path("~/.zfunc").expanduser()

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / f"_{script}").exists())

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        self.assertFalse((self.directory / f"_{script}").exists())
