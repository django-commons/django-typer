import os
from tests.utils import run_command
import time
import pytest
from pprint import pformat
from .utils import rich_installed


@pytest.mark.no_rich
@pytest.mark.skipif(
    rich_installed, reason="Rich should not be installed to test module bloat."
)
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
    result, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_no_typer"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert result["test_option"]
    assert result["no_typer"] == 5
    mods_no_typer = result["modules"]
    no_typer_time = end - start

    start = time.perf_counter()
    result, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_typer"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert result["test_option"]
    assert result["typer"] == 5
    mods_typer = result["modules"]
    typer_time = end - start

    start = time.perf_counter()
    result, stderr, retcode = run_command(
        "perf",
        "5",
        "--test-option",
        env={**env, "DJANGO_SETTINGS_MODULE": "tests.settings.perf_typer_no_app"},
    )
    end = time.perf_counter()
    if retcode:
        pytest.fail(stderr)
    assert result["test_option"]
    assert result["typer"] == 5
    mods_typer_no_app = result["modules"]
    typer_no_app_time = end - start

    # print the stats
    print("\nWithout typer:\n\t")
    print(f"\ttime: {no_typer_time:0.4f}")
    print(f"\tmodules: {len(mods_no_typer)}")

    print("\nWith typer:\n\t")
    print(f"\ttime: {typer_time:0.4f}")
    print(f"\tmodules: {len(mods_typer)}")

    print("\nWith typer, but app not installed:\n\t")
    print(f"\ttime: {typer_no_app_time:0.4f}")
    print(f"\tmodules: {len(mods_typer_no_app)}")

    # notify us if adding typer inflates module count by more than 10 percent
    assert len(mods_no_typer) / len(mods_typer) > 0.9, (
        f"Typer modules added: \n{pformat(set(mods_typer) - set(mods_no_typer))}"
    )
    assert len(mods_no_typer) / len(mods_typer_no_app) > 0.9, (
        f"Typer modules added: \n{pformat(set(mods_typer_no_app) - set(mods_no_typer))}"
    )

    # notify us if adding typer inflates command exec time by more than 50 percent
    assert no_typer_time / typer_time > 0.5
    assert no_typer_time / typer_no_app_time > 0.5
