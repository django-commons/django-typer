import djclick as click


@click.group()
@click.option("--option", default="default", help="Help text for the option")
def cli(option="default"):
    click.echo("cli(option={})".format(option))


@cli.command()
@click.argument("name")
def command1(name):
    click.echo("Hello, {}".format(name))


@cli.command()
@click.argument("model")
def command2(model):
    click.echo("model: {}".format(model))
