from django_typer.management import Typer

app = Typer()


@app.command()
def main(name: str):
    return {"name": name}
