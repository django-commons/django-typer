import typing as t

from django.apps import AppConfig, apps
from django.core.management import CommandError
from django.utils.translation import gettext as _


def app_config(label: t.Union[str, AppConfig]):
    """
    A parser for app labels. If the label is already an AppConfig instance,
    the instance is returned. The label will be tried first, if that fails
    the label will be treated as the app name.

    .. code-block:: python

        import typing as t
        import typer
        from django_typer.management import TyperCommand
        from django_typer.parsers import app_config

        class Command(TyperCommand):

            def handle(
                self,
                django_apps: t.Annotated[
                    t.List[AppConfig],
                    typer.Argument(
                        parser=app_config,
                        help=_("One or more application labels.")
                    )
                ]
            ):
                ...

    :param label: The label to map to an AppConfig instance.
    :raises CommandError: If no matching app can be found.
    """
    if isinstance(label, AppConfig):
        return label
    try:
        return apps.get_app_config(label)
    except LookupError as err:
        for cfg in apps.get_app_configs():
            if cfg.name == label:
                return cfg

        raise CommandError(
            _("{label} does not match any installed app label.").format(label=label)
        ) from err


app_config.__name__ = "APP_LABEL"
