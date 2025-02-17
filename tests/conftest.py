import pytest
from pathlib import Path


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
