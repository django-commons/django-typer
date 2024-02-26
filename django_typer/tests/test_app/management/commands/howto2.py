from django_typer import TyperCommand, command


class Command(TyperCommand):

    @command(name="subcommand1")
    def handle(self): ...

    @command()
    def subcommand2(self): ...

    @command()
    def subcommand3(self): ...
