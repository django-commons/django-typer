from django_typer.utils import (
    get_usage_script,
    accepts_var_kwargs,
    get_win_shell,
    detect_shell,
)
from django.test import override_settings
from django.core.management import call_command
from pathlib import Path
from shellingham import ShellDetectionFailure
import shutil
import pytest
import subprocess
import sys
import os


check_frame = Path(__file__).parent / "frame_check.py"


def test_get_usage_script():
    assert (
        get_usage_script("/root/path/to/scrapt")
        == Path("/root/path/to/scrapt").absolute()
    )


def test_accepts_var_kwargs():
    def func1(a, b, **kwargs): ...

    def func2(**kwargs): ...

    def func3(named=None, **kwargs): ...

    def func4(named=None): ...

    def func5(a): ...

    def func6(): ...

    assert accepts_var_kwargs(func1)
    assert accepts_var_kwargs(func2)
    assert accepts_var_kwargs(func3)
    assert not accepts_var_kwargs(func4)
    assert not accepts_var_kwargs(func5)
    assert not accepts_var_kwargs(func6)


def test_call_frame_check():
    result = subprocess.run(
        [sys.executable, str(check_frame.absolute())], text=True, capture_output=True
    )
    assert result.stdout.splitlines() == [
        "False",
        "True",
        "False",
        "True",
        "False",
        "True",
    ]


@override_settings(INSTALLED_APPS=["tests.apps.bad", "django_typer"])
def test_register_bad_command_plugin():
    with pytest.raises(ValueError):
        call_command("bad")


@pytest.mark.skipif(
    bool(shutil.which("pwsh") or shutil.which("powershell")),
    reason="Only test when pwsh is unavailable",
)
def test_get_win_shell_no_pwsh():
    with pytest.raises(ShellDetectionFailure):
        get_win_shell()


def test_detection_failure_no_env():
    shell = os.environ.pop("SHELL")
    try:
        with pytest.raises(ShellDetectionFailure):
            detect_shell(max_depth=0)
    finally:
        os.environ["SHELL"] = shell


def test_detection_env_fallback():
    shell = os.environ.pop("SHELL")
    os.environ["SHELL"] = "/bin/bash"
    try:
        assert detect_shell(max_depth=0)[0] == "bash"
    finally:
        os.environ["SHELL"] = shell


def test_detect_shell():
    assert detect_shell(max_depth=256)
