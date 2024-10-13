from django_typer.management import TyperCommand, command, group


class Command(TyperCommand):
    """
    Test that helps list commands in definition order.
    (This is different than click where the order is alphabetical by default)
    """

    @command()
    def b(self):
        print("b")

    @command()
    def a(self):
        print("a")

    @group()
    def d(self):
        print("d")

    @command()
    def c(self):
        print("c")

    @d.command()
    def g(self):
        print("g")

    def handle(self):
        print("handle")

    @d.command()
    def e(self):
        print("e")

    @d.command()
    def f(self):
        print("f")
