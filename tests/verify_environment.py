import os
import sys
from django import VERSION
from packaging.version import parse as parse_version


def test():
    # verify that the environment is set up correctly - this is used in CI to make
    # sure we're testing against the dependencies we think we are

    expected_python = os.environ["TEST_PYTHON_VERSION"]
    expected_django = os.environ["TEST_DJANGO_VERSION"]

    expected_python = parse_version(expected_python)
    assert sys.version_info[:2] == (expected_python.major, expected_python.minor), (
        f"Python Version Mismatch: {sys.version_info[:2]} != {expected_python}"
    )

    dj_actual = VERSION[:2]
    expected_django = parse_version(expected_django)
    dj_expected = (expected_django.major, expected_django.minor)
    assert dj_actual == dj_expected, (
        f"Django Version Mismatch: {dj_actual} != {expected_django}"
    )
