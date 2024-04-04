# django-typer


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/django-typer.svg)](https://pypi.python.org/pypi/django-typer/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/django-typer.svg)](https://pypi.python.org/pypi/django-typer/)
[![PyPI djversions](https://img.shields.io/pypi/djversions/django-typer.svg)](https://pypi.org/project/django-typer/)
[![PyPI status](https://img.shields.io/pypi/status/django-typer.svg)](https://pypi.python.org/pypi/django-typer)
[![Documentation Status](https://readthedocs.org/projects/django-typer/badge/?version=latest)](http://django-typer.readthedocs.io/?badge=latest/)
[![Code Cov](https://codecov.io/gh/bckohan/django-typer/branch/main/graph/badge.svg?token=0IZOKN2DYL)](https://codecov.io/gh/bckohan/django-typer)
[![Test Status](https://github.com/bckohan/django-typer/workflows/test/badge.svg)](https://github.com/bckohan/django-typer/actions/workflows/test.yml)
[![Lint Status](https://github.com/bckohan/django-typer/workflows/lint/badge.svg)](https://github.com/bckohan/django-typer/actions/workflows/lint.yml)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Use [Typer](https://typer.tiangolo.com/) to define the CLI for your [Django](https://www.djangoproject.com/) management commands. Provides a TyperCommand class that inherits from [BaseCommand](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand) and allows typer-style annotated parameter types. All of the BaseCommand functionality is preserved, so that TyperCommand can be a drop-in replacement.

**django-typer makes it easy to:**

- Define your command CLI interface in a clear, DRY, and safe way using type hints.
- Create subcommand and group command hierarchies.
- Use the full power of Typer's parameter types to validate and parse command line inputs.
- Create beautiful and information dense help outputs.
- Configure the rendering of exception stack traces using rich.
- [Install shell tab-completion support](https://django-typer.readthedocs.io/en/latest/shell_completion.html) for TyperCommands and normal Django commands for [bash](https://www.gnu.org/software/bash/), [zsh](https://www.zsh.org/), [fish](https://fishshell.com/), and [powershell](https://learn.microsoft.com/en-us/powershell/scripting/overview).
- [Create custom and portable shell tab-completions for your CLI parameters.](https://django-typer.readthedocs.io/en/latest/shell_completion.html#defining-custom-completions)
- Refactor existing management commands into TyperCommands because TyperCommand is interface compatible with BaseCommand.

Please refer to the [full documentation](https://django-typer.readthedocs.io/) for more information.

![django-typer example](https://raw.githubusercontent.com/bckohan/django-typer/main/doc/source/_static/img/closepoll_example.gif)

## Installation

1. Clone django-typer from GitHub or install a release off [PyPI](https://pypi.org/project/django-typer/):

   ```bash
   pip install django-typer
   ```

   [rich](https://rich.readthedocs.io/en/latest/) is a powerful library for rich text and beautiful formatting in the terminal. It is not required but highly recommended for the best experience:

   ```bash
   pip install "django-typer[rich]"
   ```

2. Add `django_typer` to your `INSTALLED_APPS` setting:

   ```python
   INSTALLED_APPS = [
       ...
       'django_typer',
   ]
   ```

*You only need to install django_typer as an app if you want to use the shell completion command to enable tab-completion or if you would like django-typer to install [rich traceback rendering](https://django-typer.readthedocs.io/en/latest/howto.html#configure-rich-stack-traces) for you - which it does by default if rich is also installed.*

## Basic Example

For example, TyperCommands can be a very simple drop-in replacement for BaseCommands. All of the documented features of [BaseCommand](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand) work!

```python
from django_typer import TyperCommand

class Command(TyperCommand):
    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        """
        A basic command that uses Typer
        """
```

![Basic Example](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/basic.svg)

## Multiple Subcommands Example



Commands with multiple subcommands can be defined:

```python
   import typing as t

   from django.utils.translation import gettext_lazy as _
   from typer import Argument

   from django_typer import TyperCommand, command


   class Command(TyperCommand):
      """
      A command that defines subcommands.
      """

      @command()
      def create(
         self,
         name: t.Annotated[str, Argument(help=_("The name of the object to create."))],
      ):
         """
         Create an object.
         """

      @command()
      def delete(
         self, id: t.Annotated[int, Argument(help=_("The id of the object to delete."))]
      ):
         """
         Delete an object.
         """

```

![Multiple Subcommands Example](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi.svg)
![Multiple Subcommands Example - create](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi_create.svg)
![Multiple Subcommands Example - delete](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi_delete.svg)

## Grouping and Hierarchies Example

More complex groups and subcommand hierarchies can be defined. For example, this command defines a group of commands called math, with subcommands divide and multiply. The group has a common initializer that optionally sets a float precision value. We would invoke this command like so:

```bash
./manage.py hierarchy math --precision 5 divide 10 2.1
./manage.py hierarchy math multiply 10 2
```

```python
   import typing as t
   from functools import reduce

   from django.utils.translation import gettext_lazy as _
   from typer import Argument, Option

   from django_typer import TyperCommand, group


   class Command(TyperCommand):

      help = _("A more complex command that defines a hierarchy of subcommands.")

      precision = 2

      @group(help=_("Do some math at the given precision."))
      def math(
         self,
         precision: t.Annotated[
            int, Option(help=_("The number of decimal places to output."))
         ] = precision,
      ):
         self.precision = precision

      @math.command(help=_("Multiply the given numbers."))
      def multiply(
         self,
         numbers: t.Annotated[
            t.List[float], Argument(help=_("The numbers to multiply"))
         ],
      ):
         return f"{reduce(lambda x, y: x * y, [1, *numbers]):.{self.precision}f}"

      @math.command()
      def divide(
         self,
         numerator: t.Annotated[float, Argument(help=_("The numerator"))],
         denominator: t.Annotated[float, Argument(help=_("The denominator"))],
         floor: t.Annotated[bool, Option(help=_("Use floor division"))] = False,
      ):
         """
         Divide the given numbers.
         """
         if floor:
               return str(numerator // denominator)
         return f"{numerator / denominator:.{self.precision}f}"

```

![Grouping and Hierarchies Example](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy.svg)
![Grouping and Hierarchies Example - math](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math.svg)
![Grouping and Hierarchies Example - math multiply](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math_multiply.svg)
![Grouping and Hierarchies Example - math divide](https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math_divide.svg)
