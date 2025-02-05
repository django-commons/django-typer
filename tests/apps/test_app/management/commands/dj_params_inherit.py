from django_typer.management import TyperCommand, COMMON_DEFAULTS, initialize, command
from typer.models import Context as TyperContext
from .dj_params_some_suppressed_init import Command as BaseCommand


class Command(BaseCommand):
    suppressed_base_arguments = {
        "verbosity",
        "skip_checks",
        "traceback",
        "--no-color",
        "--show-locals",
        "hide_locals",
    }

    tb: bool

    @initialize(invoke_without_command=True)
    def init(self, ctx: TyperContext, traceback: bool = True):
        self.tb = traceback
        return self.check_context(ctx, traceback)

    @command()
    def cmd(self, ctx: TyperContext):
        return self.check_context(ctx, self.tb)

    def check_context(self, ctx, traceback):
        assert self.suppressed_base_arguments
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        set(COMMON_DEFAULTS.keys())
        assert ctx.params
        assert "verbosity" not in ctx.params
        assert "skip_checks" not in ctx.params
        assert "no-color" not in ctx.params
        assert "traceback" in ctx.params
        assert "show_locals" not in ctx.params
        assert "hide_locals" not in ctx.params
        for param in COMMON_DEFAULTS.keys():
            if param not in self.suppressed_base_arguments and param not in [
                "no_color",
                "show_locals",
            ]:
                assert param in ctx.params
        return f"traceback={traceback}"
