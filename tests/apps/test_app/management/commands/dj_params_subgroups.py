from typing import Any, TextIO
from django_typer.management import (
    TyperCommand,
    COMMON_DEFAULTS,
    initialize,
    command,
    group,
)
from typer.models import Context as TyperContext


class Command(TyperCommand):
    help = "Test that django parameter suppression works as expected"

    suppressed_base_arguments = {"verbosity", "skip_checks", "traceback"}

    tb: bool

    @initialize(invoke_without_command=True)
    def init(self, ctx: TyperContext, traceback: bool = True):
        self.tb = traceback
        return self.check_context(ctx, traceback)

    @command()
    def cmd(self, ctx: TyperContext):
        return self.check_context(ctx, self.tb)

    @group(invoke_without_command=True)
    def subgroup(self, ctx: TyperContext, skip_checks: bool = True):
        return self.check_context(ctx, self.tb, skip_checks=skip_checks)

    def check_context(self, ctx, traceback, skip_checks=None):
        assert self.suppressed_base_arguments
        assert self.__class__ is Command
        assert isinstance(ctx, TyperContext)
        set(COMMON_DEFAULTS.keys())
        assert ctx.params
        assert "verbosity" not in ctx.params
        assert (
            "skip_checks" not in ctx.params
            if skip_checks is None
            else "skip_checks" in ctx.params
        )
        assert "traceback" in ctx.params
        for param in COMMON_DEFAULTS.keys():
            if param not in self.suppressed_base_arguments:
                assert param in ctx.params
        return f"traceback={traceback}, skipchecks={skip_checks}"