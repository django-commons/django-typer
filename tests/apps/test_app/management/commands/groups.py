import typing as t

from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer.management import TyperCommand, command, group


class Command(TyperCommand):
    help = _("Test multiple groups commands and callbacks")

    precision = 2
    verbosity = 1

    @command()
    def echo(self, message: str) -> str:
        """
        Echo the given message.
        """
        assert issubclass(self.__class__, Command)
        return message

    @group()
    def math(self, precision: int = precision):
        """
        Do some math at the given precision.
        """
        assert issubclass(self.__class__, Command)
        self.precision = precision

    @math.command()
    def multiply(
        self,
        number1: t.Annotated[
            float, Argument(help=_("The first number."), show_default=False)
        ],
        number2: t.Annotated[
            float, Argument(help=_("The second number."), show_default=False)
        ],
        numbers: t.Annotated[
            t.List[float],
            Argument(
                help=_("The list of numbers to multiply: n1*n2*n3*...*nN. "),
                show_default=False,
            ),
        ],
    ):
        """
        Multiply the given numbers.
        """
        assert issubclass(self.__class__, Command)
        res = number1 * number2
        for n in numbers:
            res *= n
        return f"{res:.{self.precision}f}"

    @math.command()
    def divide(
        self,
        number1: t.Annotated[
            float, Argument(help=_("The numerator."), show_default=False)
        ],
        number2: t.Annotated[
            float, Argument(help=_("The denominator."), show_default=False)
        ],
        numbers: t.Annotated[
            t.List[float],
            Argument(
                help=_("Additional denominators: n1/n2/n3/.../nN."), show_default=False
            ),
        ],
    ) -> str:
        """
        Divide the given numbers.
        """
        assert issubclass(self.__class__, Command)
        res = number1 / number2
        for n in numbers:
            res /= n
        return f"{res:.{self.precision}f}"

    @group()
    def string(
        self,
        string: t.Annotated[
            str, Argument(help=_("The string to operate on."), show_default=False)
        ],
    ):
        """
        String operations.
        """
        assert issubclass(self.__class__, Command)
        self.op_string = string

    @string.group()
    def case(self):
        """
        Case operations.
        """
        assert issubclass(self.__class__, Command)

    @case.command()
    def upper(
        self,
        begin: t.Annotated[
            int, Argument(help=_("The starting index of the string to operate on."))
        ] = 0,
        end: t.Annotated[
            t.Optional[int],
            Argument(help=_("The ending index of the string to operate on.")),
        ] = None,
    ) -> str:
        """
        Convert the given string to upper case.
        """
        assert issubclass(self.__class__, Command)
        return f"{self.op_string[0:begin]}{self.op_string[begin:end].upper()}{self.op_string[end:None] if end else ''}"

    @case.command()
    def lower(
        self,
        begin: t.Annotated[
            int, Option(help=_("The starting index of the string to operate on."))
        ] = 0,
        end: t.Annotated[
            t.Optional[int],
            Option(help=_("The ending index of the string to operate on.")),
        ] = None,
    ):
        """
        Convert the given string to upper case.
        """
        assert issubclass(self.__class__, Command)
        return f"{self.op_string[0:begin]}{self.op_string[begin:end].lower()}{self.op_string[end:None] if end else ''}"

    @string.command()
    def split(self, sep: str = " "):
        """
        Split the given string on the given separator.
        """
        assert issubclass(self.__class__, Command)
        return " ".join(self.op_string.split(sep))

    def test(self, a: int, b: int) -> int:
        return a + b
