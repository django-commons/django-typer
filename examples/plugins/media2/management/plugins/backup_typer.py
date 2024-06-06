import tarfile
import typing as t
from pathlib import Path

import typer
from django.conf import settings

from tests.apps.examples.plugins.backup.management.commands import (
    backup_typer,
)


# for typer-style plugins we use the decorators on the root Typer app directly
@backup_typer.app.command()
def media(
    # self is optional, but if you want to access the command instance, you
    # can specify it
    self,
    filename: t.Annotated[
        str,
        typer.Option(
            "-f",
            "--filename",
            help=("The name of the file to use for the media backup tar."),
        ),
    ] = "media.tar.gz",
):
    """
    Backup the media files (i.e. those files in MEDIA_ROOT).
    """
    media_root = Path(settings.MEDIA_ROOT)
    output_file = self.output_directory / filename

    # backup the media directory into the output file as a gzipped tar
    typer.echo(f"Backing up {media_root} to {output_file}")
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(media_root, arcname=media_root.name)
