from click import get_current_context

from django_typer import TyperCommand, command, initialize


class Command(TyperCommand):

    help = "Test handle as initializer."

    @initialize(invoke_without_command=True)
    def handle(self):
        if (ctx := get_current_context(silent=True)) and ctx.invoked_subcommand:
            return

        # if we're here a subcommand was not invoked
        return "handle"

    @command()
    def subcommand(self):
        return "subcommand"
