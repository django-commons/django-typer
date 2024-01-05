import json
import typing as t

from typer import Argument

from django_typer import TyperCommand, command, group


class Command(TyperCommand):
    help = "Test multiple groups commands and callbacks"

    precision = 2
    verbosity = 1

    @command()
    def echo(self, message: str):
        """
        Echo the given message.
        """
        assert self.__class__ is Command
        return json.dumps({"echo": message})

    @group()
    def math(self, precision: int = precision):
        """
        Do some math at the given precision.
        """
        assert self.__class__ is Command
        self.precision = precision

    @math.command()
    def multiply(
        self,
        number1: t.Annotated[
            float, Argument(help="The first number.", show_default=False)
        ],
        number2: t.Annotated[
            float, Argument(help="The second number.", show_default=False)
        ],
        numbers: t.Annotated[
            t.List[float],
            Argument(
                help=("The list of numbers to multiple: n1*n2*n3*...*nN. "),
                show_default=False,
            ),
        ],
    ):
        """
        Multiply the given numbers.
        """
        assert self.__class__ is Command
        res = number1 * number2
        for n in numbers:
            res *= n
        return json.dumps({"multiply": f"{res:.{self.precision}f}"})

    @math.command()
    def divide(
        self,
        number1: t.Annotated[
            float, Argument(help="The numerator.", show_default=False)
        ],
        number2: t.Annotated[
            float, Argument(help="The denominator.", show_default=False)
        ],
        numbers: t.Annotated[
            t.List[float],
            Argument(
                help=("Additional denominators: n1/n2/n3/.../nN. "), show_default=False
            ),
        ],
    ):
        """
        Divide the given numbers.
        """
        assert self.__class__ is Command
        res = number1 / number2
        for n in numbers:
            res /= n
        return json.dumps({"divide": f"{res:.{self.precision}f}"})

    @group()
    def string(
        self,
        string: t.Annotated[
            str, Argument(help="The string to operate on.", show_default=False)
        ],
    ):
        """
        String operations.
        """
        assert self.__class__ is Command
        self.op_string = string

    @string.group()
    def case(self):
        """
        Case operations.
        """
        assert self.__class__ is Command

    @case.command()
    def upper(
        self,
        begin: t.Annotated[int, Argument()] = 0,
        end: t.Annotated[t.Optional[int], Argument()] = None,
    ):
        """
        Convert the given string to upper case.
        """
        assert self.__class__ is Command
        return json.dumps(
            {
                "upper": f'{self.op_string[0:begin]}{self.op_string[begin:end].upper()}{self.op_string[end:None] if end else ""}'
            }
        )

    @case.command()
    def lower(
        self,
        begin: t.Annotated[int, Argument()] = 0,
        end: t.Annotated[t.Optional[int], Argument()] = None,
    ):
        """
        Convert the given string to upper case.
        """
        assert self.__class__ is Command
        return json.dumps(
            {
                "lower": f'{self.op_string[0:begin]}{self.op_string[begin:end].lower()}{self.op_string[end:None] if end else ""}'
            }
        )

    @string.command()
    def split(self, sep: str = " "):
        """
        Split the given string on the given separator.
        """
        assert self.__class__ is Command
        return json.dumps({"split": self.op_string.split(sep)})
