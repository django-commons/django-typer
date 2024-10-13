from django_typer.management import TyperCommand, command, group, initialize
from .inheritance2_1 import Command as Inheritance21Command
from .inheritance2_2 import Command as Inheritance22Command


class Command(Inheritance21Command, Inheritance22Command):
    @command()
    def b(self):
        assert isinstance(self, Command)
        return "inheritance3::b()"

    @command()
    def d(self):
        assert isinstance(self, Command)
        return "inheritance3::d()"

    @Inheritance22Command.g2.command()
    def g2a(self):
        assert isinstance(self, Command)
        return "inheritance3::g2::g2a()"
