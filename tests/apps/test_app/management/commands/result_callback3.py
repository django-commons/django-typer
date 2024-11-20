from django_typer.management import Typer


def finalize(self: "Command", **_):
    assert isinstance(self, Command)
    return "finalize"


app = Typer(result_callback=finalize)


@app.callback(result_callback=finalize)
def callback(self):
    assert isinstance(self, Command)
    return self


@app.command()
def cmd(self):
    assert isinstance(self, Command)
    return self
