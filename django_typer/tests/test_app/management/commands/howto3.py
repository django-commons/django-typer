from django_typer import TyperCommand, command
from django_typer import initialize as root


class Command(TyperCommand):

    @root(invoke_without_command=True)
    def handle(self, flag: bool = False):
        # This is the root command, it runs when we run our command without
        # any subcommand
        print(flag)

    @command()
    def subcommand1(self):
        pass

    @command()
    def subcommand2(self):
        pass
