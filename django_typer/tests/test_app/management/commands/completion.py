import json
import typing as t
from functools import partial

import typer
from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _

from django_typer import TyperCommand


def parse_app_label(label: t.Union[str, AppConfig]):
    if label == "django_apps":
        import ipdb

        ipdb.set_trace()
    if isinstance(label, AppConfig):
        return label
    return apps.get_app_config(label)


def complete_app_label(ctx: typer.Context, incomplete: str):
    names = ctx.params.get("django_apps") or []
    for name in [app.label for app in apps.get_app_configs()]:
        if name.startswith(incomplete) and name not in names:
            yield name


class Command(TyperCommand):
    def handle(
        self,
        django_apps: t.Annotated[
            t.List[AppConfig],
            typer.Argument(
                parser=parse_app_label,
                help=_("One or more application labels."),
                autocompletion=complete_app_label,
            ),
        ],
    ):
        assert self.__class__ == Command
        for app in django_apps:
            assert isinstance(app, AppConfig)
        return json.dumps([app.label for app in django_apps])
