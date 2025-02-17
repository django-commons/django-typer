from django_typer.management import TyperCommand, COMMON_DEFAULTS
from typer.models import Context as TyperContext
from tests.utils import rich_installed


class Command(TyperCommand):
    help = "Test that django parameter suppression works as expected"

    suppressed_base_arguments = []

    def handle(self, ctx: TyperContext):
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        assert not set(ctx.params.keys()).symmetric_difference(
            [
                key
                for key in COMMON_DEFAULTS.keys()
                if key
                not in ["hide_locals", *(["show_locals"] if not rich_installed else [])]
            ]
        )
