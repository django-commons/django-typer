from django_typer.management import TyperCommand, COMMON_DEFAULTS, initialize, command
from typer.models import Context as TyperContext


class Command(TyperCommand):
    help = "Test that django parameter suppression works as expected"

    suppressed_base_arguments = set(COMMON_DEFAULTS.keys())

    @initialize()
    def init(self, ctx: TyperContext):
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        assert not ctx.params

    @command(name="cmd")
    def handle(self, ctx: TyperContext):
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        assert not ctx.params
