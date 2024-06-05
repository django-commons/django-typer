from django_typer import TyperCommand


class Command(TyperCommand):
    def handle(self, message: str):
        assert isinstance(self, Command)
        self.echo(f"test_app: {message}")
