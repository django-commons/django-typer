import typer

from django_typer.management import Typer

app = Typer()


@app.command()
def handle(self):
    self.echo("echo does not support styling")
    self.secho("but secho does!", fg=typer.colors.GREEN)
