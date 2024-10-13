import sys
import typing as t
from pathlib import Path

import typer
import pluggy

from tests.apps.examples.plugins.media1.management.commands.backup import (
    Command as Backup,
)


class Command(Backup):  # inherit from the extended media backup command
    plugins = pluggy.PluginManager("backup")
    hookspec = pluggy.HookspecMarker("backup")
    hookimpl = pluggy.HookimplMarker("backup")

    # add a new command called files that delegates file backups to plugins
    @Backup.command()
    def files(self):
        """
        Backup app specific non-media files.
        """
        for archive in self.plugins.hook.backup_files(command=self):
            if archive:
                typer.echo(f"Backed up files to {archive}")


@Command.hookspec
def backup_files(command: Command) -> t.Optional[Path]:
    """
    A hook for backing up app specific files.

    Must return the path to the archive file or None if no files were backed up.

    :param command: the backup command instance
    :return: The path to the archived backup file
    """


Command.plugins.add_hookspecs(sys.modules[__name__])
