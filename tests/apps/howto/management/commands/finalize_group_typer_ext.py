from django_typer.management import Typer

# Use extensions to the typer interface to improve clarity

app = Typer(chain=True)


@app.finalize()
def to_csv(results):
    return ", ".join(results)


@app.group(chain=True)
def grp():
    pass


@grp.finalize()
def to_upper_csv(results):
    return ", ".join([result.upper() for result in results])


@app.command()
def cmd1():
    return "result1"


@app.command()
def cmd2():
    return "result2"


@grp.command()
def cmd3():
    return "result3"


@grp.command()
def cmd4():
    return "result4"
