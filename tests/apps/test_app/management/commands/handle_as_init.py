from click import get_current_context

from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    help = "Test handle as initializer."

    @initialize(invoke_without_command=True)
    def handle(self):
        assert self.__class__ is Command
        if (ctx := get_current_context(silent=True)) and ctx.invoked_subcommand:
            return

        # if we're here a subcommand was not invoked
        return "handle"

    @command()
    def subcommand(self):
        assert self.__class__ is Command
        return "subcommand"
