import typing as t

from django.apps import AppConfig, apps
from django.core.management import CommandError


def app_config(label: t.Union[str, AppConfig]):
    """
    A parser for app :attr:`~django.apps.AppConfig.label`. If the label is already
    an :class:`~django.apps.AppConfig` instance, the instance is returned. The label
    will be tried first, if that fails the label will be treated as the app
    :attr:`~django.apps.AppConfig.name`.

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

        raise CommandError(f"{label} does not match any installed app label.") from err


app_config.__name__ = "APP_LABEL"
