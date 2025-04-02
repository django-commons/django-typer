import shutil
from pathlib import Path
import typing as t

import pytest
from django.test import TestCase, override_settings
import sys
import os
import platform

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

    def verify_install(self, script=None, directory: t.Optional[Path] = None):
        directory = directory or self.directory
        if not script:
            script = self.manage_script
        self.assertTrue((directory / f"_{script}").exists())

    def verify_remove(self, script=None, directory: t.Optional[Path] = None):
        directory = directory or self.directory
        if not script:
            script = self.manage_script
        self.assertFalse((directory / f"_{script}").exists())


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
            os.unlink(Path.home() / ".zshrc")
            self.remove()
            self.verify_remove()
        finally:
            if zshrc:
                (Path.home() / ".zshrc").write_text(zshrc)

    @override_settings(TEMPLATES=[])
    def test_no_template_config(self):
        self.test_shell_complete()

    if platform.system() != "Windows":

        def test_prompt_install(self, env={}, directory=None):
            zdot_dir = Path(__file__).parent / "zdotdir"
            try:
                zdot_dir.mkdir(exist_ok=True)
                super().test_prompt_install(
                    env={"ZDOTDIR": str(zdot_dir.absolute())},
                    directory=zdot_dir / ".zfunc",
                )
            finally:
                if zdot_dir.exists():
                    shutil.rmtree(zdot_dir)
