"""
Test that multi-level and multiple inheritance resolves correctly.
"""

from django_typer.management import TyperCommand, command, group, initialize


class Command(TyperCommand):
    """
    Inheritance1
    """

    @initialize(invoke_without_command=True)
    def init(self):
        assert isinstance(self, Command)
        return "inheritance1::init()"

    @command()
    def a(self):
        assert isinstance(self, Command)
        return "inheritance1::a()"

    @group(invoke_without_command=True)
    def g(self):
        assert isinstance(self, Command)
        return "inheritance1::g()"

    @g.command()
    def ga(self):
        assert isinstance(self, Command)
        return "inheritance1::g::ga()"

    @g.command()
    def gb(self):
        assert isinstance(self, Command)
        return "inheritance1::g::gb()"
