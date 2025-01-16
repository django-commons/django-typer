import importlib
import inspect
import typing as t

import typer.core
from django.apps import AppConfig, apps
from django.core.management.base import CommandError

from django_typer.management import Typer, TyperCommand, get_command
from django_typer import completers, parsers, utils

from pathlib import Path

import graphviz
import typer


try:
    from enum import StrEnum

    class Format(StrEnum):
        png = "png"
        svg = "svg"
        pdf = "pdf"
        dot = "dot"

except ImportError:
    from enum import Enum

    class Format(str, Enum):
        png = "png"
        svg = "svg"
        pdf = "pdf"
        dot = "dot"

        def __str__(self):
            return self.value


class Command(TyperCommand):
    """
    Graph the Typer app tree associated with the given command.
    """

    cmd: TyperCommand
    cmd_name: str
    app_name: str
    plugin: t.Optional[str] = None
    dot = graphviz.Digraph()
    level: int = -1
    show_ids: bool = False
    seen = set()

    def handle(
        self,
        commands: t.Annotated[
            t.List[str],
            typer.Argument(
                help="Import path(s) to the command to graph, or simply the name of the command.",
                shell_complete=completers.chain(
                    completers.complete_import_path,
                    completers.commands(allow_duplicates=True),
                    allow_duplicates=True,
                ),
            ),
        ],
        output: t.Annotated[
            Path,
            typer.Option(
                "-o",
                "--output",
                help="The path to save the graph to.",
                shell_complete=completers.complete_path,
            ),
        ] = Path("{command}_app_tree"),
        format: t.Annotated[
            Format,
            typer.Option(
                "-f",
                "--format",
                help="The format to save the graph in.",
                shell_complete=completers.these_strings(list(Format)),
            ),
        ] = Format.png,
        show_ids: t.Annotated[
            bool, typer.Option(help="Show the object identifiers.")
        ] = show_ids,
        instantiate: t.Annotated[
            bool,
            typer.Option(help="Instantiate the command before graphing the app tree."),
        ] = True,
        load_order: t.Annotated[
            t.List[AppConfig],
            typer.Option(
                "-l",
                "--load",
                parser=parsers.parse_app_label,
                shell_complete=completers.complete_app_label,
                help="Load plugins from these apps after each command is graphed in the order provided.",
            ),
        ] = [],
    ):
        assert len(load_order) <= len(commands), (
            "Cannot provide more load options than commands"
        )

        plugin_loads = []

        for app in load_order:
            to_load = {}
            for cmd, plugins in list(utils._command_plugins.items()):
                to_load[cmd] = []
                for plugin in list(plugins):
                    if (
                        self.get_app_from_module(plugin.__name__.split(".")[0:-2])
                        == app
                    ):
                        to_load[cmd].append(plugin)
            plugin_loads.append(to_load)

        if load_order:
            utils._command_plugins = {}

        self.show_ids = show_ids
        for command in commands:
            self.level = -1
            self.cmd_name = command.split(".")[-1]
            if "." in command:
                self.cmd = getattr(importlib.import_module(command), "Command")
                if instantiate:
                    self.cmd = self.cmd()
            elif instantiate:
                self.cmd = get_command(command, TyperCommand)
            else:
                raise CommandError("Cannot instantiate a command that is not imported.")

            self.app_name = self.get_app_from_module(
                self.cmd.__module__.split(".")[0:-3]
            ).name

            output = Path(output.parent) / Path(
                output.name.format(command=self.cmd_name)
            )

            self.visit_app(self.cmd.typer_app)

            of = output.parent / f"{output.stem}.{format}"
            num = 1
            while of.exists():
                of = output.parent / f"{output.stem}({num}).{format}"
                num += 1
            self.dot.render(of.parent / of.stem, format=format, view=len(commands) == 1)
            if load_order:
                utils._command_plugins = plugin_loads.pop(0)
                self.plugin = load_order.pop(0).name.split(".")[-1]
            else:
                self.plugin = None

    def get_app_from_module(self, module: t.List[str]) -> t.Optional[AppConfig]:
        app = importlib.import_module(f"{'.'.join(module)}.apps")
        for _, attr in vars(app).items():
            if (
                inspect.isclass(attr)
                and issubclass(attr, AppConfig)
                and attr is not AppConfig
            ):
                return apps.get_app_config(getattr(attr, "label", module[-1]))

    def get_node_name(self, obj: t.Union[typer.models.CommandInfo, Typer]):
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
        if self.show_ids:
            return f"[{hex(id(obj))[-4:]}] {name}"
        return name

    def visit_app(self, app: Typer):
        """
        Walk the typer app tree.
        """
        self.level += 1
        if self.level:
            parent_node = self.get_node_name(app)
        else:
            plugin = f": {self.plugin}" if self.plugin else ""
            parent_node = f"[{self.app_name.split('.')[-1]}{plugin}] {self.cmd_name}"

        style = {}
        if self.level:
            style = {"style": "filled", "fillcolor": "lightblue"}
        self.dot.node(str(id(app)), parent_node, **style)
        for cmd in app.registered_commands:
            node_name = self.get_node_name(cmd)
            self.dot.node(str(id(cmd)), node_name, style="filled", fillcolor="green")
            edge = (str(id(app)), str(id(cmd)))
            if edge not in self.seen:
                self.seen.add(edge)
                self.dot.edge(*edge)
        for grp in app.registered_groups:
            assert grp.typer_instance
            node_name = self.get_node_name(t.cast(Typer, grp.typer_instance))
            edge = str(id(app)), str(id(grp.typer_instance))
            if edge not in self.seen:
                self.seen.add(edge)
                self.dot.edge(*edge)
            self.visit_app(t.cast(Typer, grp.typer_instance))
