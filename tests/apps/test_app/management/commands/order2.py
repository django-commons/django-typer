from django_typer.management import TyperCommand, command, group
from tests.apps.test_app.management.commands.order import Command as OrderCommand


class Command(OrderCommand):
    """
    Test that helps list commands in definition order.
    (This is different than click where the order is alphabetical by default)
    """

    @group()
    def bb(self):
        print("bb")

    @command()
    def aa(self):
        print("aa")

    @OrderCommand.d.group()
    def x(self):
        print("x")

    @command()
    def b(self):
        print("b")

    @OrderCommand.d.command()
    def i(self):
        print("i")

    @OrderCommand.d.command()
    def h(self):
        print("h")

    @command(help="Override handle")
    def handle(self):
        print("handle")

    @x.command()
    def z(self):
        print("z")

    @x.command()
    def y(self):
        print("y")
