import click
from pprint import pprint


params = {}

@click.group(context_settings={'allow_interspersed_args': True, 'ignore_unknown_options': True})
@click.argument("name")
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
def main(name: str, verbose: bool = False):
    """
    Help text for the main command
    """
    global params
    params = {"name": name, "verbose": verbose}


@main.command()
@click.argument("arg1")
@click.argument("arg2")
@click.option("--flag1", "-f", is_flag=True, help="A flag.")
def command1(arg1, arg2, flag1=False):
    global params
    params.update({"arg1": arg1, "arg2": arg2, "flag1": flag1})
    pprint(params)


if __name__ == "__main__":
    main()
