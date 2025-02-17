from django_typer.management import Typer

# use native Typer interface to achieve the same result


def to_csv(results, **_):
    return ", ".join(results)


def to_upper_csv(results, **_):
    return ", ".join([result.upper() for result in results])


app = Typer(result_callback=to_csv, chain=True)

grp = Typer(result_callback=to_upper_csv, chain=True)
app.add_typer(grp, name="grp")


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
