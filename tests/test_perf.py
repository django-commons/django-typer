import os
from tests.utils import run_command
import time
import pytest


def test_performance_regression():
    env = dict(os.environ)

    # disable coverage
    for var in [
        "COVERAGE_PROCESS_START",
        "COV_CORE_SOURCE",
        "COV_CORE_CONFIG",
        "COV_CORE_DATAFILE",
        "PYTEST_XDIST_WORKER",
    ]:
        env.pop(var, None)

    start = time.perf_counter()
    stdout, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_no_typer"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert "test_option=True" in stdout
    assert "no_typer: 5" in stdout
    mods_no_typer = int(stdout.split(",")[-1].strip())
    no_typer_time = end - start

    start = time.perf_counter()
    stdout, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_typer"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert "test_option=True" in stdout
    assert "typer: 5" in stdout
    mods_typer = int(stdout.split(",")[-1].strip())
    typer_time = end - start

    start = time.perf_counter()
    stdout, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_typer_no_app"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert "test_option=True" in stdout
    assert "typer: 5" in stdout
    mods_typer_no_app = int(stdout.split(",")[-1].strip())
    typer_no_app_time = end - start

    # print the stats
    print("\nWithout typer:\n\t")
    print(f"\ttime: {no_typer_time:0.4f}")
    print(f"\tmodules: {mods_no_typer}")

    print("\nWith typer:\n\t")
    print(f"\ttime: {typer_time:0.4f}")
    print(f"\tmodules: {mods_typer}")

    print("\nWith typer, but app not installed:\n\t")
    print(f"\ttime: {typer_no_app_time:0.4f}")
    print(f"\tmodules: {mods_typer_no_app}")

    # notify us if adding typer inflates module count by more than 10 percent
    assert mods_no_typer / mods_typer > 0.9
    assert mods_no_typer / mods_typer_no_app > 0.9

    # notify us if adding typer inflates command exec time by more than 20 percent
    assert no_typer_time / typer_time > 0.75
    assert no_typer_time / typer_no_app_time > 0.75
