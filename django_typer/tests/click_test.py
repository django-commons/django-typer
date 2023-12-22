import click


@click.group()
def cli():
    """
    Help text for the main command
    """
    print("cli()")


@cli.command()
def command1():
    click.echo("command1")


@cli.command()
@click.argument("model")
def command2(model):
    click.echo("model: {}".format(model), fg="red")


if __name__ == "__main__":
    cli()
