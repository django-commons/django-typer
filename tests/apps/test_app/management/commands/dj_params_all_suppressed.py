from django_typer.management import TyperCommand, COMMON_DEFAULTS
from typer.models import Context as TyperContext


class Command(TyperCommand):
    help = "Test that django parameter suppression works as expected"

    suppressed_base_arguments = set(COMMON_DEFAULTS.keys())

    def handle(self, ctx: TyperContext):
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        assert not ctx.params
