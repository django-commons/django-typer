from django_typer.management import TyperCommand, command


class Command(TyperCommand, chain=True, no_args_is_help=True):
    @command()
    def command1(self):
        return "command1"

    @command()
    def command2(self):
        return "command2"
