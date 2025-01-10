import warnings


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
