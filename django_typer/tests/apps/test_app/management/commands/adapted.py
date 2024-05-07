import json


from django_typer import TyperCommand


class Command(TyperCommand):
    def handle(self, message: str):
        self.echo(f"test_app: {message}")
