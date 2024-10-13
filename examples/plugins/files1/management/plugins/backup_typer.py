import sys
import typing as t
from pathlib import Path

from tests.apps.examples.plugins.backup_files.management.commands.backup_typer import (
    plugins,
    hookimpl,
)


@hookimpl
def backup_files(command) -> t.Optional[Path]:
    # this is where you would put your custom file backup logic
    return command.output_directory / "files1.tar.gz"


plugins.register(sys.modules[__name__])
