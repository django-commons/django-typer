import json
import typing as t

import typer
from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _

from django_typer import TyperCommand, completers, parsers


class Command(TyperCommand):
    def handle(
        self,
        django_apps: t.Annotated[
            t.List[AppConfig],
            typer.Argument(
                parser=parsers.parse_app_label,
                help=_("One or more application labels."),
                shell_complete=completers.complete_app_label,
            ),
        ],
    ):
        assert self.__class__ == Command
        for app in django_apps:
            assert isinstance(app, AppConfig)
        return json.dumps([app.label for app in django_apps])
