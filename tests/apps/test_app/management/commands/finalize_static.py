from django_typer.management import TyperCommand, finalize


class Command(TyperCommand):
    @finalize()
    @staticmethod
    def final(result, traceback: bool = False):
        assert result == "handle"
        return f"finalized: {result} | traceback={traceback}"

    def handle(self):
        return "handle"
