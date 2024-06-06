from django_typer.management import Typer, TyperCommand

Command: TyperCommand

app = Typer()


@app.command()
def main(self, name: str):
    assert isinstance(self, TyperCommand)
    return {"name": name}
