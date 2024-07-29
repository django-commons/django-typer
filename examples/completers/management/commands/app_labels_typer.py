import typing as t
import typer
from click import Context, Parameter
from click.shell_completion import CompletionItem
from django.apps import apps

from django_typer.management import Typer

app = Typer()


# the completer function signature must match this exactly
def complete_app_label(
    ctx: Context, param: Parameter, incomplete: str
) -> t.List[CompletionItem]:
    # don't offer apps that are already present as completion suggestions
    present = [app.label for app in (ctx.params.get(param.name or "") or [])]
    return [
        CompletionItem(app.label)
        for app in apps.get_app_configs()
        if app.label.startswith(incomplete) and app.label not in present
    ]


@app.command()
def handle(
    apps: t.Annotated[
        t.List[str],
        typer.Argument(
            help="The app label",
            # pass the completer function here
            shell_complete=complete_app_label,
        ),
    ],
):
    print(apps)
