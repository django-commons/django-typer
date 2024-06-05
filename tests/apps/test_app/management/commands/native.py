from django_typer import Typer

app = Typer()


@app.command()
def main(name: str):
    return {"name": name}
