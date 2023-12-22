import typer

from django_typer import TyperCommandWrapper, _common_options

app = typer.Typer(epilog="Typer Epilog")


@app.command(epilog="Main Epilog")
def main(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")


if __name__ == "__main__":
    app()
