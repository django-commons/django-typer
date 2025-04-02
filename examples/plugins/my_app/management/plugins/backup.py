import datetime
import shutil
import subprocess
import typing as t

import typer
from django.conf import settings

from tests.apps.examples.plugins.backup.management.commands.backup import (
    Command as Backup,
)


@Backup.command()
def environment(
    self,
    filename: t.Annotated[
        str,
        typer.Option(
            "-f",
            "--filename",
            help=("The name of the requirements file."),
        ),
    ] = "requirements.txt",
):
    """
    Capture the python environment using pip freeze.
    """

    output_file = self.output_directory / filename

    typer.echo(f"Capturing python environment to {output_file}")
    with output_file.open("w") as f:
        subprocess.run(["uv", "pip", "freeze"], stdout=f)


@Backup.command()
def database(self):
    """
    Backup the database by copying the sqlite file and tagging it with the
    current date.
    """
    db_file = self.output_directory / f"backup_{datetime.date.today()}.sqlite3"
    self.echo("Backing up database to {db_file}")
    shutil.copy(
        settings.DATABASES["default"]["NAME"],
        db_file,
    )
