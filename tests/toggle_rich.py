import os
import re
import pytest


def _marker_in_markexpr(markexpr: str, marker: str) -> bool:
    # cheap/ok heuristic: whole-word match in the expression
    return bool(re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", markexpr or ""))


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    """toggle rich on/off based on test markers"""
    markexpr = ""
    for i, a in enumerate(args):
        if a == "-m" and i + 1 < len(args):
            markexpr = args[i + 1]
            break
        if a.startswith("-m") and len(a) > 2:
            markexpr = a[2:]
            break

    # Toggle rich early based on explicit "no_rich" / "rich" markers in the -m expression
    if not _marker_in_markexpr(markexpr, "no_rich"):
        if not _marker_in_markexpr(markexpr, "rich"):
            return
        else:
            use_rich = True
    else:
        use_rich = False

    os.environ["TYPER_USE_RICH"] = "1" if use_rich else "0"
    from tests import utils

    utils.rich_installed = use_rich
