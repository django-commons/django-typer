import inspect
import os
import typing as t
from pathlib import Path

import typer
from django.conf import settings
from django.core.management import CommandError, call_command

from django_typer.management import CommandNode, Typer
from django_typer.completers.path import directories
from django_typer.completers.db import databases as complete_db

app = Typer()

# these two lines are not necessary but will make your type checker happy
assert app.django_command
Command = app.django_command

Command.suppressed_base_arguments = {"verbosity", "skip_checks"}
Command.requires_migrations_checks = False
Command.requires_system_checks = []

databases = [alias for alias in settings.DATABASES.keys()]


@app.callback(invoke_without_command=True)
def init_or_run_all(
    self,
    # if we add a context argument Typer will provide it
    # the context is a click object that contains additional
    # information about the broader CLI invocation
    context: typer.Context,
    output_directory: t.Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            shell_complete=directories,
            help="The directory to write backup artifacts to.",
        ),
    ] = Path(os.getcwd()),
):
    """
    Backup the website! This command groups backup routines together.
    Each routine may be run individually, but if no routine is specified,
    the default run of all routines will be executed.
    """
    self.output_directory = output_directory

    if not self.output_directory.exists():
        self.output_directory.mkdir(parents=True)

    if not self.output_directory.is_dir():
        raise CommandError(f"{self.output_directory} is not a directory.")

    # here we use the context to determine if a subcommand was invoked and
    # if it was not we run all the backup routines
    if not context.invoked_subcommand:
        for cmd in get_backup_routines(self):
            cmd()


@app.command()
def list(self):
    """
    List the default backup routines in the order they will be run.
    """
    self.echo("Default backup routines:")
    for cmd in get_backup_routines(self):
        sig = {
            name: param.default
            for name, param in inspect.signature(
                cmd.callback
            ).parameters.items()
            if not name == "self"
        }
        params = ", ".join([f"{k}={v}" for k, v in sig.items()])
        self.secho(f"  {cmd.name}({params})", fg="green")


@app.command()
def database(
    self,
    filename: t.Annotated[
        str,
        typer.Option(
            "-f",
            "--filename",
            help=(
                "The name of the file to use for the backup fixture. The "
                "filename may optionally contain a {database} formatting "
                "placeholder."
            ),
        ),
    ] = "{database}.json",
    databases: t.Annotated[
        t.Optional[t.List[str]],
        typer.Option(
            "-d",
            "--database",
            help=(
                "The name of the database(s) to backup. If not provided, "
                "all databases will be backed up."
            ),
            shell_complete=complete_db(),
        ),
    ] = databases,
):
    """
    Backup database(s) to a json fixture file.
    """
    for db in databases or self.databases:
        output = self.output_directory / filename.format(database=db)
        self.echo(f"Backing up database [{db}] to: {output}")
        call_command(
            "dumpdata",
            output=output,
            database=db,
            format="json",
        )


def get_backup_routines(command) -> t.List[CommandNode]:
    """
    Return the list of backup subcommands. This is every registered command
    except for the list command.
    """
    # fetch all the command names at the top level of our command tree,
    # except for list, which we know to not be a backup routine
    return [
        cmd
        for name, cmd in command.get_subcommand().children.items()
        if name != "list"
    ]
