from django_typer.management import Typer

app = Typer()

app.django_command.print_result = False


@app.command()
def handle():
    return "This will not be printed"
