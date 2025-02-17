from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    @command()
    def cmd1(self):
        pass

    @command()
    def cmd2(self):
        pass
