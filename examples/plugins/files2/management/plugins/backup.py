import sys
import typing as t
from pathlib import Path

from tests.apps.examples.plugins.backup_files.management.commands.backup import (
    Command as Backup,
)


@Backup.hookimpl
def backup_files(command: Backup) -> t.Optional[Path]:
    # this is where you would put your custom file backup logic
    return command.output_directory / "files2.zip"


Backup.plugins.register(sys.modules[__name__])
