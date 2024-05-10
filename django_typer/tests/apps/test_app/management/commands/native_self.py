from django_typer import Typer, TyperCommand

app = Typer()


@app.command()
def main(self, name: str):
    assert isinstance(self, TyperCommand)
    return {"name": name}
