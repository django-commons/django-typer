from django_typer.management import TyperCommand, command, group, initialize
from .inheritance1 import Command as Inheritance1Command


class Command(Inheritance1Command):
    """
    Inheritance2_2
    """

    @initialize(invoke_without_command=True)
    def init(self):
        assert isinstance(self, Command)
        return "inheritance2_2::init()"

    @command()
    def a(self):
        assert isinstance(self, Command)
        return "inheritance2_2::a()"

    @command()
    def b(self):
        assert isinstance(self, Command)
        return "inheritance2_2::b()"

    @command()
    def c(self):
        assert isinstance(self, Command)
        return "inheritance2_2::c()"

    @group()
    def g(self):
        assert isinstance(self, Command)
        return "inheritance2_2::g()"

    @g.command()
    def ga(self):
        assert isinstance(self, Command)
        return "inheritance2_2::g::ga()"

    @group(invoke_without_command=True)
    def g2(self):
        assert isinstance(self, Command)
        return "inheritance2_2::g2()"
