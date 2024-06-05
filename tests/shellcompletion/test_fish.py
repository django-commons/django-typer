import os
import shutil
import sys
from pathlib import Path

import pytest
from django.test import TestCase

from tests.shellcompletion import (
    _DefaultCompleteTestCase,
    _InstalledScriptTestCase,
)


@pytest.mark.skipif(shutil.which("fish") is None, reason="Fish not available")
class FishShellTests(_DefaultCompleteTestCase):  # , TestCase):
    """
    TODO this test is currently disabled because fish completion installation does
    not seem to work for scripts not on the path.
    """

    shell = "fish"
    directory = Path("~/.config/fish/completions").expanduser()

    def set_environment(self, fd):
        # super().set_environment(fd)
        os.write(fd, f"export PATH={Path(sys.executable).parent}:$PATH\n".encode())
        os.write(
            fd,
            f'export DJANGO_SETTINGS_MODULE={os.environ["DJANGO_SETTINGS_MODULE"]}\n'.encode(),
        )

    def verify_install(self, script=None):
        if not script:
            script = self.manage_script
        self.assertTrue((self.directory / f"{script}.fish").exists())

    def verify_remove(self, script=None):
        if not script:
            script = self.manage_script
        self.assertFalse((self.directory / f"{script}.fish").exists())

    def test_shell_complete(self):
        # just verify that install/remove works. The actual completion is not tested
        # because there's an issue running fish interactively in a pty:
        #  warning: No TTY for interactive shell (tcgetpgrp failed)
        #  setpgid: Inappropriate ioctl for device
        # TODO - fix this
        self.install()
        self.remove()


@pytest.mark.skipif(shutil.which("fish") is None, reason="Fish not available")
class FishExeShellTests(_InstalledScriptTestCase, FishShellTests, TestCase):
    shell = "fish"
