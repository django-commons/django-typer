import os
import sys
import django


def test():
    # verify that the environment is set up correctly - this is used in CI to make
    # sure we're testing against the dependencies we think we are

    expected_python = os.environ["TEST_PYTHON_VERSION"]
    expected_django = os.environ["TEST_DJANGO_VERSION"]

    expected_python = tuple(int(v) for v in expected_python.split(".") if v)
    assert sys.version_info[: len(expected_python)] == expected_python, (
        f"Python Version Mismatch: {sys.version_info[: len(expected_python)]} != "
        f"{expected_python}"
    )

    try:
        expected_django = tuple(int(v) for v in expected_django.split(".") if v)
        assert django.VERSION[: len(expected_django)] == expected_django, (
            f"Django Version Mismatch: {django.VERSION[: len(expected_django)]} != "
            f"{expected_django}"
        )
    except ValueError:
        assert expected_django == django.__version__
