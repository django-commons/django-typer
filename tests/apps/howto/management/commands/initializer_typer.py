from django_typer.management import Typer

app = Typer()


# initializers are called callbacks in Typer, but we may also use initialize()
# as an alias
@app.callback()
def init(self, common_option: bool = False):
    # you can define common options that will be available to all subcommands
    # of the command, and implement common initialization logic here. This
    # will be invoked before the chosen command
    self.common_option = common_option


@app.command()
def subcommand1(self):
    return self.common_option


@app.command()
def subcommand2(self):
    return self.common_option
