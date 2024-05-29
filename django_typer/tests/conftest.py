# conftest.py
def pytest_collection_modifyitems(items):
    """Modifies test items in place to ensure test modules run in a given order."""
    sorted_tests = []
    interference_tests = []
    adapter_tests = []  # push these to the back

    for test in items:
        if "plugin" in test.module.__name__:
            adapter_tests.append(test)
        elif "test_interference" in test.module.__name__:
            interference_tests.append(test)
        else:
            sorted_tests.append(test)

    items[:] = [
        *sorted_tests,
        *adapter_tests,
        *interference_tests,
    ]
