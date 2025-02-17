from django_typer.management import Typer, TyperCommand

Command: TyperCommand

app = Typer()

# safe to use Command after first Typer() call
Command.suppressed_base_arguments = {
    "--skip-checks",
    "traceback",
    "force_color",
    "--show-locals",
}


@app.command()
def main(name: str):
    return {"name": name}
