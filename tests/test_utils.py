from django_typer.utils import get_usage_script
from pathlib import Path


def test_get_usage_script():
    assert get_usage_script("/root/path/to/script") == Path("/root/path/to/script")
