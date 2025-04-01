import json
import typing as t
from pathlib import Path
from typing import Annotated
from functools import partial

import typer
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from django_typer.management import TyperCommand
from django_typer.completers.apps import app_labels
from django_typer.parsers.apps import app_config
from django_typer.completers.path import (
    directories,
    paths,
    import_paths,
    static_paths,
    media_paths,
)
from django_typer.completers.settings import setting, languages
from django_typer.completers.db import databases
from django_typer.completers.cmd import commands
from django_typer.completers import these_strings, chain
from django_typer.types import COMMON_PANEL


settings_dir = Path(__file__).parent.parent.parent.parent.parent / "settings"


class Command(TyperCommand, rich_markup_mode="rich"):
    def handle(
        self,
        django_apps: Annotated[
            t.List[AppConfig],
            typer.Argument(
                help=t.cast(str, _("One or more application labels.")),
                parser=app_config,
                shell_complete=app_labels,
            ),
        ],
        option: Annotated[
            t.Optional[AppConfig],
            typer.Option(
                parser=app_config,
                help=t.cast(str, _("An app given as an option.")),
                shell_complete=app_labels,
            ),
        ] = None,
        path: Annotated[
            t.Optional[Path],
            typer.Option(
                help=t.cast(str, _("A path given as an option.")),
                shell_complete=paths,
            ),
        ] = None,
        dir: Annotated[
            t.Optional[Path],
            typer.Option(
                help=t.cast(str, _("A directory given as an option.")),
                shell_complete=directories,
            ),
        ] = None,
        strings_unique: Annotated[
            t.Optional[t.List[str]],
            typer.Option(
                "--str",
                help=t.cast(str, _("A list of unique strings.")),
                shell_complete=these_strings(["str1", "str2", "ustr"]),
            ),
        ] = None,
        strings_duplicates: Annotated[
            t.Optional[t.List[str]],
            typer.Option(
                "--dup",
                help=t.cast(str, _("A list of strings that can have duplicates.")),
                shell_complete=these_strings(
                    ["str1", "str2", "ustr"], allow_duplicates=True
                ),
            ),
        ] = None,
        commands: Annotated[
            t.List[str],
            typer.Option(
                "--cmd",
                help=t.cast(
                    str,
                    _("A command by [bold]import path[/bold] or [bold]name[/bold]."),
                ),
                shell_complete=chain(import_paths, commands()),
            ),
        ] = [],
        command_dups: Annotated[
            t.List[str],
            typer.Option(
                "--cmd-dup",
                help=t.cast(
                    str,
                    _("A list of [reverse]commands[/reverse] by import path or name."),
                ),
                shell_complete=chain(
                    import_paths, commands(allow_duplicates=True), allow_duplicates=True
                ),
            ),
        ] = [],
        command_first: Annotated[
            t.List[str],
            typer.Option(
                "--cmd-first",
                help=t.cast(
                    str,
                    _(
                        "A list of [yellow][underline]commands[/underline][/yellow] by either import path or name."
                    ),
                ),
                shell_complete=chain(
                    import_paths, commands(allow_duplicates=True), first_match=True
                ),
            ),
        ] = [],
        app_opt: Annotated[
            t.List[str],
            typer.Option(
                help=t.cast(str, _("One or more application labels.")),
                shell_complete=app_labels,
            ),
        ] = ["test_app"],
        databases: Annotated[
            t.List[str],
            typer.Option(
                "--db",
                help=t.cast(str, _("One or more database aliases.")),
                shell_complete=databases(),
            ),
        ] = [],
        statics: Annotated[
            t.Optional[Path],
            typer.Option(
                help=t.cast(str, _("Static files.")),
                shell_complete=static_paths,
            ),
        ] = None,
        media: Annotated[
            t.Optional[Path],
            typer.Option(
                help=t.cast(str, _("Media files.")),
                shell_complete=media_paths,
            ),
        ] = None,
        settings_module: Annotated[
            str,
            typer.Option(
                help=t.cast(
                    str,
                    ("The python path to the settings file under tests.settings."),
                ),
                rich_help_panel=COMMON_PANEL,
                shell_complete=partial(import_paths, root=settings_dir),
                show_default=False,
            ),
        ] = "",
        languages: Annotated[
            t.List[str],
            typer.Option(
                "--lang",
                help=t.cast(str, _("One or more languages.")),
                shell_complete=languages,
            ),
        ] = [],
        setting: Annotated[
            t.List[str],
            typer.Option(
                "--setting",
                help=t.cast(str, _("One or more Django setting variables.")),
                shell_complete=setting,
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
