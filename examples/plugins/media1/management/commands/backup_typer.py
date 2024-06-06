import tarfile
import typing as t
from pathlib import Path

import typer
from django.conf import settings

from django_typer.management import Typer
from tests.apps.examples.plugins.backup.management.commands import (
    backup_typer,
)

# to inherit all commands defined upstream pass the root typer app from upstream
# to our root app here. (This is not a standard typer interface.)
app = Typer(backup_typer.app)


@app.command()
def media(
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
