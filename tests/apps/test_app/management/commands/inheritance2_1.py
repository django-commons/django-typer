from django_typer.management import TyperCommand, command, group, initialize
from .inheritance1 import Command as Inheritance1Command


class Command(Inheritance1Command):
    """
    Inheritance2_1
    """

    @initialize(invoke_without_command=True)
    def init(self):
        assert isinstance(self, Command)
        return "inheritance2_1::init()"

    @command()
    def a(self):
        assert isinstance(self, Command)
        return "inheritance2_1::a()"

    @command()
    def b(self):
        assert isinstance(self, Command)
        return "inheritance2_1::b()"

    @group()
    def g(self):
        assert isinstance(self, Command)
        return "inheritance2_1::g()"

    @g.command()
    def ga(self):
        assert isinstance(self, Command)
        return "inheritance2_1::g::ga()"

    @g.command()
    def gb(self):
        assert isinstance(self, Command)
        return "inheritance2_1::g::gb()"

    @g.command()
    def gc(self):
        assert isinstance(self, Command)
        return "inheritance2_1::g::gc()"
