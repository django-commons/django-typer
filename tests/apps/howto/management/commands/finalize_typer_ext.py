from django_typer.management import Typer

# alternatively we can use the finalize nomenclature of the TyperCommand
# interface - this is a non-standard Typer extension

app = Typer(chain=True)


# The Typer interface is extended with the finalize decorator
@app.finalize()
def to_csv(results):
    return ", ".join(results)


@app.command()
def cmd1():
    return "result1"


@app.command()
def cmd2():
    return "result2"
