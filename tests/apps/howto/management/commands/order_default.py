from .order import Command as Order
from django_typer.management import group


class Command(Order):
    @group()
    def d(self):
        print("d")

    @d.command()
    def f(self):
        print("f")

    @d.command()
    def e(self):
        print("e")
