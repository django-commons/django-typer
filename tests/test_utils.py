from django_typer.utils import (
    get_usage_script,
    accepts_var_kwargs,
    get_win_shell,
    detect_shell,
    parse_iso_duration,
    duration_iso_string,
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


@pytest.mark.skipif(
    bool(shutil.which("pwsh") or shutil.which("powershell")),
    reason="Only test when pwsh is unavailable",
)
def test_powershell_profile_fail():
    from django_typer.shells.powershell import PowerShellComplete

    with pytest.raises(Exception):
        PowerShellComplete().get_user_profile()


def test_detection_failure_no_env():
    shell = os.environ.pop("SHELL", "")
    try:
        with pytest.raises(ShellDetectionFailure):
            detect_shell(max_depth=0)
    finally:
        os.environ["SHELL"] = shell


def test_detection_env_fallback():
    shell = os.environ.pop("SHELL", "")
    os.environ["SHELL"] = "/bin/bash"
    try:
        assert detect_shell(max_depth=0)[0] == "bash"
    finally:
        os.environ["SHELL"] = shell


def test_detect_shell():
    assert detect_shell(max_depth=256)


def test_parse_iso_duration():
    from datetime import timedelta

    for duration in [
        timedelta(days=3, hours=4, minutes=30, seconds=15, microseconds=123456),
        timedelta(days=1, hours=12, minutes=0, seconds=0),
        timedelta(days=0, hours=23, minutes=45, seconds=30),
        timedelta(days=5, hours=0, minutes=15, seconds=5, microseconds=987654),
        timedelta(days=2, hours=8, minutes=0, seconds=0),
        -timedelta(days=3, hours=4, minutes=30, seconds=15, microseconds=123456),
        -timedelta(days=1, hours=12, minutes=0, seconds=0),
        -timedelta(days=2, hours=20, minutes=10, seconds=30),
        -timedelta(days=5, hours=6, minutes=0, seconds=50, microseconds=123000),
        -timedelta(days=10, hours=5, minutes=55, seconds=5),
        timedelta(),
        timedelta(days=1),
        timedelta(hours=2),
        timedelta(minutes=3),
        timedelta(seconds=4),
        timedelta(microseconds=5),
    ]:
        assert parse_iso_duration(duration_iso_string(duration)) == (duration, None)

    assert parse_iso_duration("") == (timedelta(), None)
    assert parse_iso_duration("-") == (-timedelta(), None)
    assert parse_iso_duration("+") == (timedelta(), None)

    with pytest.raises(ValueError):
        parse_iso_duration("?")

    with pytest.raises(ValueError):
        parse_iso_duration("=")

    with pytest.raises(ValueError):
        parse_iso_duration("P10DX1S")

    with pytest.raises(ValueError):
        parse_iso_duration("P10DT5H.43S")

    assert parse_iso_duration("-P2DT12H") == (-timedelta(days=2, hours=12), None)
    assert parse_iso_duration("P1") == (timedelta(), "1")
    assert parse_iso_duration("PT1") == (timedelta(), "1")
    assert parse_iso_duration("P2DT2H4") == (timedelta(days=2, hours=2), "4")
    assert parse_iso_duration("P2DT2H4M5") == (
        timedelta(days=2, hours=2, minutes=4),
        "5",
    )
    assert parse_iso_duration("P2DT2H4M5.") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5),
        None,
    )

    # microseconds are weird
    assert parse_iso_duration("P2DT2H4M5.000123") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=123),
        None,
    )
    assert parse_iso_duration("P2DT2H4M5.123456") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=123456),
        None,
    )

    assert parse_iso_duration("P2DT2H4M5.000123S") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=123),
        None,
    )
    assert parse_iso_duration("P2DT2H4M5.123456S") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=123456),
        None,
    )

    assert parse_iso_duration("P2DT2H4M5.00012") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5),
        "00012",
    )
    assert parse_iso_duration("P2DT2H4M5.12") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5),
        "12",
    )

    assert parse_iso_duration("P2DT2H4M5.00012S") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=120),
        None,
    )
    assert parse_iso_duration("P2DT2H4M5.12S") == (
        timedelta(days=2, hours=2, minutes=4, seconds=5, microseconds=120000),
        None,
    )

    assert parse_iso_duration("P2DT5.00012S") == (
        timedelta(days=2, seconds=5, microseconds=120),
        None,
    )
    assert parse_iso_duration("P2DT5.12S") == (
        timedelta(days=2, seconds=5, microseconds=120000),
        None,
    )

    assert parse_iso_duration("P2DT5.00012") == (timedelta(days=2, seconds=5), "00012")
    assert parse_iso_duration("P2DT5.12") == (timedelta(days=2, seconds=5), "12")

    assert parse_iso_duration("P2DT5.") == (timedelta(days=2, seconds=5), None)
    assert parse_iso_duration("P2DT5.") == (timedelta(days=2, seconds=5), None)

    assert parse_iso_duration("PT5") == (timedelta(), "5")
    assert parse_iso_duration("-PT5") == (-timedelta(), "5")
