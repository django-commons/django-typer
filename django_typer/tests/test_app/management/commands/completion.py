import json
import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

import typer
from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _

from django_typer import TyperCommand, completers, parsers


class Command(TyperCommand):
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
    ):
        assert self.__class__ == Command
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
