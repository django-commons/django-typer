import pytest
from pathlib import Path
import inspect
import os
import sys
from django import VERSION
from packaging.version import parse as parse_version


# conftest.py
def pytest_collection_modifyitems(items):
    """Modifies test items in place to ensure plugin tests run in a specific order."""
    sorted_tests = []
    interference_tests = []
    plugin_tests = []  # push these to the back
    native_plugin_tests = []

    for test in items:
        if "plugin_pattern" in test.module.__name__:
            plugin_tests.append(test)
        elif "native_plugin" in test.module.__name__:
            native_plugin_tests.append(test)
        elif "test_interference" in test.module.__name__:
            interference_tests.append(test)
        else:
            sorted_tests.append(test)

    items[:] = [
        *sorted_tests,
        *plugin_tests,
        *native_plugin_tests,
        *interference_tests,
    ]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    log_file = Path(__file__).parent / "tests.log"
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.outcome == "passed":
        if log_file.exists():
            with open(log_file, "a") as log_file:
                log_file.write(f"{item.nodeid}\n")


def first_breakable_line(obj) -> tuple[str, int]:
    """
    Return the absolute line number of the first executable statement
    in a function or bound method.
    """
    import ast
    import textwrap

    func = obj.__func__ if inspect.ismethod(obj) else obj

    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    filename = inspect.getsourcefile(func)
    assert filename
    _, start_lineno = inspect.getsourcelines(func)

    tree = ast.parse(source)

    for node in tree.body[0].body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue

        return filename, start_lineno + node.lineno - 1

    # fallback: just return the line after the def
    return filename, start_lineno + 1


def pytest_runtest_call(item):
    # --trace cli option does not work for unittest style tests so we implement it here
    test = getattr(item, "obj", None)
    if item.config.option.trace and inspect.ismethod(test):
        from IPython.terminal.debugger import TerminalPdb

        try:
            file = inspect.getsourcefile(test)
            assert file
            dbg = TerminalPdb()
            dbg.set_break(*first_breakable_line(test))
            dbg.cmdqueue.append("continue")
            dbg.set_trace()
        except (OSError, AssertionError):
            pass


def pytest_configure(config: pytest.Config) -> None:

    if os.getenv("GITHUB_ACTIONS") == "true":
        # verify that the environment is set up correctly - this is used in CI to make
        # sure we're testing against the dependencies we think we are
        expected_python = os.getenv("TEST_PYTHON_VERSION")
        expected_django = os.getenv("TEST_DJANGO_VERSION")

        if expected_python:
            expected_python = parse_version(expected_python)
            if sys.version_info[:2] != (expected_python.major, expected_python.minor):
                raise pytest.UsageError(
                    f"Python Version Mismatch: {sys.version_info[:2]} != "
                    f"{expected_python}"
                )

        if expected_django:
            dj_actual = VERSION[:2]
            expected_django = parse_version(expected_django)
            dj_expected = (expected_django.major, expected_django.minor)
            if dj_actual != dj_expected:
                raise pytest.UsageError(
                    f"Django Version Mismatch: {dj_actual} != {expected_django}"
                )
