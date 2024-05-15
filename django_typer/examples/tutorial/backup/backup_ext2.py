import subprocess
import typing as t

import typer

from django_typer.tests.apps.backup.backup.management.commands.backup import (
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
        subprocess.run(["pip", "freeze"], stdout=f)
