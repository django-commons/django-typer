from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    def finalize(self, **kwargs):
        assert isinstance(self, Command)
        return "finalized"

    @initialize(result_callback=finalize)
    def init(self):
        return "init"

    @command()
    def cmd(self):
        return self
