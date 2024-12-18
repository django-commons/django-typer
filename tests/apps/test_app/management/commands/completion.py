import json
import typing as t
from pathlib import Path
from typing import Annotated

import typer
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from django_typer.management import TyperCommand
from django_typer import completers, parsers


class Command(TyperCommand, rich_markup_mode="rich"):
    def handle(
        self,
        django_apps: Annotated[
            t.List[AppConfig],
            typer.Argument(
                parser=parsers.parse_app_label,
                help=_("One or more application labels."),
                shell_complete=completers.complete_app_label,
            ),
        ],
        option: Annotated[
            t.Optional[AppConfig],
            typer.Option(
                parser=parsers.parse_app_label,
                help=_("An app given as an option."),
                shell_complete=completers.complete_app_label,
            ),
        ] = None,
        path: Annotated[
            t.Optional[Path],
            typer.Option(
                help=_("A path given as an option."),
                shell_complete=completers.complete_path,
            ),
        ] = None,
        strings_unique: Annotated[
            t.Optional[t.List[str]],
            typer.Option(
                "--str",
                help=_("A list of unique strings."),
                shell_complete=completers.these_strings(["str1", "str2", "ustr"]),
            ),
        ] = None,
        strings_duplicates: Annotated[
            t.Optional[t.List[str]],
            typer.Option(
                "--dup",
                help=_("A list of strings that can have duplicates."),
                shell_complete=completers.these_strings(
                    ["str1", "str2", "ustr"], allow_duplicates=True
                ),
            ),
        ] = None,
        commands: Annotated[
            t.List[str],
            typer.Option(
                "--cmd",
                help=_("A command by [bold]import path[/bold] or [bold]name[/bold]."),
                shell_complete=completers.chain(
                    completers.complete_import_path, completers.commands()
                ),
            ),
        ] = [],
        command_dups: Annotated[
            t.List[str],
            typer.Option(
                "--cmd-dup",
                help=_("A list of [reverse]commands[/reverse] by import path or name."),
                shell_complete=completers.chain(
                    completers.complete_import_path,
                    completers.commands(allow_duplicates=True),
                    allow_duplicates=True,
                ),
            ),
        ] = [],
        command_first: Annotated[
            t.List[str],
            typer.Option(
                "--cmd-first",
                help=_(
                    "A list of [yellow][underline]commands[/underline][/yellow] by import path or name."
                ),
                shell_complete=completers.chain(
                    completers.complete_import_path,
                    completers.commands(allow_duplicates=True),
                    first_match=True,
                ),
            ),
        ] = [],
        app_opt: Annotated[
            t.List[str],
            typer.Option(
                help=_("One or more application labels."),
                shell_complete=completers.complete_app_label,
            ),
        ] = ["test_app"],
        databases: Annotated[
            t.List[str],
            typer.Option(
                "--db",
                help=_("One or more database aliases."),
                shell_complete=completers.databases(),
            ),
        ] = [],
    ):
        assert self.__class__ is Command
        for app in django_apps:
            assert isinstance(app, AppConfig)
        if option:
            return json.dumps(
                {
                    "django_apps": [app.label for app in django_apps],
                    "option": option.label,
                }
            )
        return json.dumps([app.label for app in django_apps])
