from django_typer.management import Typer


def to_csv(results, **_):
    # result_callback is passed the CLI parameters on the current context
    # if we are uninterested in them, we can use the **_ syntax to ignore them
    return ", ".join(results)


app = Typer(result_callback=to_csv, chain=True)


@app.command()
def cmd1():
    return "result1"


@app.command()
def cmd2():
    return "result2"
