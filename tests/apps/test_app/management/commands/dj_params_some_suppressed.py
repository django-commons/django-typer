from django_typer.management import TyperCommand, COMMON_DEFAULTS, initialize, command
from typer.models import Context as TyperContext


class Command(TyperCommand):
    help = "Test that django parameter suppression works as expected"

    suppressed_base_arguments = {
        "verbosity",
        "skip_checks",
        "traceback",
        "show_locals",
        "hide_locals",
    }

    def handle(self, ctx: TyperContext, traceback: bool = True):
        assert self.suppressed_base_arguments
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        set(COMMON_DEFAULTS.keys())
        assert ctx.params
        assert "verbosity" not in ctx.params
        assert "skip_checks" not in ctx.params
        assert "traceback" in ctx.params
        for param in COMMON_DEFAULTS.keys():
            if param not in self.suppressed_base_arguments:
                assert param in ctx.params
        return f"traceback={traceback}"
