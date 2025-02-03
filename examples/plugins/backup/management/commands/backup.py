import inspect
import os
import typing as t
from pathlib import Path

import typer
from django.conf import settings
from django.core.management import CommandError, call_command

from django_typer.management import (
    CommandNode,
    TyperCommand,
    command,
    initialize,
)
from django_typer.completers.db import databases as complete_db
from django_typer.completers.path import directories


class Command(TyperCommand):
    """
    Backup the website! This command groups backup routines together.
    Each routine may be run individually, but if no routine is specified,
    the default run of all routines will be executed.
    """

    suppressed_base_arguments = {"verbosity", "skip_checks"}

    requires_migrations_checks = False
    requires_system_checks = []

    databases = [alias for alias in settings.DATABASES.keys()]

    output_directory: Path

    @initialize(invoke_without_command=True)
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
        self.output_directory = output_directory

        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)

        if not self.output_directory.is_dir():
            raise CommandError(f"{self.output_directory} is not a directory.")

        # here we use the context to determine if a subcommand was invoked and
        # if it was not we run all the backup routines
        if not context.invoked_subcommand:
            for cmd in self.get_backup_routines():
                cmd()

    def get_backup_routines(self) -> t.List[CommandNode]:
        """
        Return the list of backup subcommands. This is every registered command
        except for the list command.
        """
        # fetch all the command names at the top level of our command tree,
        # except for list, which we know to not be a backup routine
        return [
            cmd
            for name, cmd in self.get_subcommand().children.items()
            if name != "list"
        ]

    @command()
    def list(self):
        """
        List the default backup routines in the order they will be run.
        """
        self.echo("Default backup routines:")
        for cmd in self.get_backup_routines():
            sig = {
                name: param.default
                for name, param in inspect.signature(
                    cmd.callback
                ).parameters.items()
                if not name == "self"
            }
            params = ", ".join([f"{k}={v}" for k, v in sig.items()])
            self.secho(f"  {cmd.name}({params})", fg="green")

    @command()
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
            t.List[str],
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
