from django_typer.management import TyperCommand, command, finalize


class Command(TyperCommand):
    @finalize()
    def final(self, result, **_):
        assert isinstance(self, Command)
        assert result == "handle"
        return "finalized: {}".format(result)

    def handle(self):
        return "handle"
