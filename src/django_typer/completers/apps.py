import typing as t

from click import Context, Parameter
from click.core import ParameterSource
from click.shell_completion import CompletionItem
from django.apps import apps


def app_labels(
    ctx: Context, param: Parameter, incomplete: str
) -> t.List[CompletionItem]:
    """
    A case-sensitive completer for Django app labels or names. The completer
    prefers labels but names will also work.

    .. code-block:: python

        import typing as t
        import typer
        from django_typer.management import TyperCommand
        from django_typer.parsers import parse_app_label
        from django_typer.completers import complete_app_label

        class Command(TyperCommand):

            def handle(
                self,
                django_apps: t.Annotated[
                    t.List[AppConfig],
                    typer.Argument(
                        parser=parse_app_label,
                        shell_complete=complete_app_label,
                        help=_("One or more application labels.")
                    )
                ]
            ):
                ...

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :return: A list of matching app labels or names. Labels already present for the
        parameter on the command line will be filtered out.
    """
    present = []
    if (
        param.name
        and ctx.get_parameter_source(param.name) is not ParameterSource.DEFAULT
    ):
        present = [app.label for app in (ctx.params.get(param.name) or [])]
    ret = [
        CompletionItem(app.label)
        for app in apps.get_app_configs()
        if app.label.startswith(incomplete) and app.label not in present
    ]
    if not ret and incomplete:
        ret = [
            CompletionItem(app.name)
            for app in apps.get_app_configs()
            if app.name.startswith(incomplete)
            and app.name not in present
            and app.label not in present
        ]
    return ret
