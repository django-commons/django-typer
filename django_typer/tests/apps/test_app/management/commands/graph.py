import typing as t
from django.core.management.base import CommandError
import typer.core
from django_typer import TyperCommand, completers, get_command, Typer, CommandGroup
import importlib
import sys

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

import typer
from pathlib import Path

import graphviz


from enum import StrEnum


class Format(StrEnum):
    png = "png"
    svg = "svg"
    pdf = "pdf"
    dot = "dot"


class Command(TyperCommand):
    """
    Graph the Typer app tree associated with the given command.
    """

    cmd: TyperCommand
    cmd_name: str
    dot = graphviz.Digraph()
    level: int = -1

    def handle(
        self,
        command: Annotated[
            str,
            typer.Argument(
                help="An import path to the command to graph, or simply the name of the command.",
                shell_complete=completers.complete_import_path,
            ),
        ],
        output: Annotated[
            Path,
            typer.Option(
                "-o",
                "--output",
                help="The path to save the graph to.",
                shell_complete=completers.complete_path,
            ),
        ] = Path("{command}_app_tree"),
        format: Annotated[
            Format,
            typer.Option(
                "-f",
                "--format",
                help="The format to save the graph in.",
                shell_complete=completers.these_strings(list(Format)),
            ),
        ] = Format.png,
        instantiate: Annotated[
            bool,
            typer.Option(help="Instantiate the command before graphing the app tree."),
        ] = True,
    ):
        self.cmd_name = command.split(".")[-1]
        if "." in command:
            self.cmd = getattr(importlib.import_module(command), "Command")
            if instantiate:
                self.cmd = self.cmd()
        elif instantiate:
            self.cmd = get_command(command, TyperCommand)
        else:
            raise CommandError("Cannot instantiate a command that is not imported.")

        output = Path(output.parent) / Path(output.name.format(command=self.cmd_name))

        self.visit_app(self.cmd.typer_app)
        self.dot.render(output, format=format, view=True)

    def get_node_name(self, obj: t.Union[typer.models.CommandInfo, CommandGroup]):
        assert obj.callback
        name = (
            obj.callback.__name__
            if isinstance(obj, typer.models.CommandInfo)
            else str(obj.name)
        )
        cli_name = (
            obj.name or name
            if isinstance(obj, typer.models.CommandInfo)
            else obj.info.name or name
        )
        if name != cli_name:
            name += f"({cli_name})"
        return f"[{hex(id(obj))[-4:]}] {name}"

    def visit_app(self, app: Typer):
        """
        Walk the typer app tree.
        """
        self.level += 1
        parent_node = self.get_node_name(app) if self.level else self.cmd_name

        self.dot.node(str(id(app)), parent_node)
        for cmd in app.registered_commands:
            node_name = self.get_node_name(cmd)
            self.dot.node(str(id(cmd)), node_name)
            self.dot.edge(str(id(app)), str(id(cmd)))
        for grp in app.registered_groups:
            assert grp.typer_instance
            node_name = self.get_node_name(t.cast(CommandGroup, grp.typer_instance))
            self.dot.edge(str(id(app)), str(id(grp.typer_instance)))
            self.visit_app(t.cast(Typer, grp.typer_instance))
