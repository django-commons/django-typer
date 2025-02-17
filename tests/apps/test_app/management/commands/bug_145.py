from django_typer.management import Typer

app = Typer()

grp = Typer()
app.add_typer(grp, name="grp")


@grp.command()
def cmd():
    return "grp:cmd"
