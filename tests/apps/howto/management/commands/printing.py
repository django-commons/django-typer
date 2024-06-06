import typer

from django_typer.management import TyperCommand


class Command(TyperCommand):
    def handle(self):
        self.echo("echo does not support styling")
        self.secho("but secho does!", fg=typer.colors.GREEN)
