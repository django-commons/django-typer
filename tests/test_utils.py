from django_typer.utils import get_usage_script, accepts_var_kwargs, get_win_shell
from pathlib import Path
from shellingham import ShellDetectionFailure
import platform
import pytest
import subprocess
import sys


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


@pytest.mark.skipif(platform.system() == "Windows", reason="Only test off Windows")
def test_get_win_shell_wrong_platform():
    with pytest.raises(ShellDetectionFailure):
        get_win_shell()


def test_call_frame_check():
    result = subprocess.run(
        [sys.executable, str(check_frame.absolute())], text=True, capture_output=True
    )
    assert result.stdout.splitlines() == ["False", "True", "False", "True"]
