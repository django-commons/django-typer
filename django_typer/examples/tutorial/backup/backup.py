import inspect
import os
import typing as t
from pathlib import Path

import typer
from django.conf import settings
from django.core.management import CommandError, call_command

from django_typer import TyperCommand, command, completers, initialize


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

    DEFAULT_DATABASE_FILENAME = "{database}.json"

    output_directory: Path

    @initialize(invoke_without_command=True)
    def default(
        self,
        context: typer.Context,
        output_directory: t.Annotated[
            Path,
            typer.Option(
                "-o",
                "--output",
                shell_complete=completers.complete_directory,
                help="The directory to write backup artifacts to.",
            ),
        ] = Path(os.getcwd()),
    ):
        self.output_directory = output_directory

        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)

        if not self.output_directory.is_dir():
            raise CommandError(f"{self.output_directory} is not a directory.")

        if not context.invoked_subcommand:
            for cmd in self.get_default_routines():
                getattr(self, cmd)()

    def get_default_routines(self) -> t.List[str]:
        """
        Return the list of backup subcommands. This is every registered command except for the
        list command.
        """
        return [cmd for cmd in self.get_subcommand().children.keys() if cmd != "list"]

    @command()
    def list(self):
        """
        List the default backup routines in the order they will be run.
        """
        self.echo("Default backup routines:")
        for cmd in self.get_default_routines():
            kwargs = {
                name: str(param.default)
                for name, param in inspect.signature(
                    getattr(self, cmd)
                ).parameters.items()
            }
            params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.secho(f"  {cmd}({params})", fg="green")

    @command()
    def database(
        self,
        filename: t.Annotated[
            str,
            typer.Option(
                "-f",
                "--filename",
                help=(
                    "The name of the file to use for the backup fixture. The filename may "
                    "optionally contain a {database} formatting placeholder."
                ),
            ),
        ] = DEFAULT_DATABASE_FILENAME,
        databases: t.Annotated[
            t.Optional[t.List[str]],
            typer.Option(
                "-d",
                "--database",
                help=(
                    "The name of the database(s) to backup. If not provided, all databases "
                    "will be backed up."
                ),
                shell_complete=completers.databases,
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
