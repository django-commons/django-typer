#!/usr/bin/env python3

"""
Determines if any tests were not run based on the logs.
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    test_log = Path(__file__).parent / "tests.log"
    all_tests = Path(__file__).parent / "all_tests.log"
    assert test_log.is_file() and all_tests.is_file()

    tests_run = set(test_log.read_text().splitlines())
    all_tests = set(all_tests.read_text().splitlines()[0:-2])
    if tests_run != all_tests:
        print("Not all tests were run:", file=sys.stderr)
        for test in all_tests - tests_run:
            print(test, file=sys.stderr)
        sys.exit(1)
