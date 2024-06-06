from django_typer.management import Typer

# here we pass chain=True to typer telling it to allow invocation of
# multiple subcommands
app = Typer(chain=True)


@app.command()
def cmd1(self):
    self.stdout.write("cmd1")


@app.command()
def cmd2(self):
    self.stdout.write("cmd2")
