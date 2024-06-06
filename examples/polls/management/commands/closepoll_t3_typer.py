import typing as t

from django.core.management.base import CommandError
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer.management import Typer
from tests.apps.examples.polls.models import Question as Poll


def get_poll_from_id(poll: t.Union[str, Poll]) -> Poll:
    if isinstance(poll, Poll):
        return poll
    try:
        return Poll.objects.get(pk=int(poll))
    except Poll.DoesNotExist:
        raise CommandError(f'Poll "{poll}" does not exist')


app = Typer(rich_markup_mode="markdown")


@app.command()
def handle(
    self,
    polls: t.Annotated[
        t.List[Poll],
        Argument(
            parser=get_poll_from_id,
            help=_("The database IDs of the poll(s) to close."),
        ),
    ],
    delete: t.Annotated[
        bool,
        Option(
            "--delete",  # we can also get rid of that unnecessary --no-delete flag
            help=_("Delete poll instead of closing it."),
        ),
    ] = False,
):
    """
    :sparkles: As mentioned in the last section, helps can also be set in
    the docstring and rendered using either
    [rich](https://rich.readthedocs.io/en/stable/markup.html)
    or [markdown](https://www.markdownguide.org/) :sparkles:
    """
    for poll in polls:
        poll.opened = False
        poll.save()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
        )
        if delete:
            poll.delete()
