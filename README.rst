|MIT license| |PyPI version fury.io| |PyPI pyversions| |PyPi djversions| |PyPI status| |Documentation Status|
|Code Cov| |Test Status| |Lint Status| |Code Style|

.. |MIT license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://lbesson.mit-license.org/

.. |PyPI version fury.io| image:: https://badge.fury.io/py/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer/

.. |PyPI djversions| image:: https://img.shields.io/pypi/djversions/django-typer.svg
   :target: https://pypi.org/project/django-typer/

.. |PyPI status| image:: https://img.shields.io/pypi/status/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer

.. |Documentation Status| image:: https://readthedocs.org/projects/django-typer/badge/?version=latest
   :target: http://django-typer.readthedocs.io/?badge=latest/

.. |Code Cov| image:: https://codecov.io/gh/bckohan/django-typer/branch/main/graph/badge.svg?token=0IZOKN2DYL
   :target: https://codecov.io/gh/bckohan/django-typer

.. |Test Status| image:: https://github.com/bckohan/django-typer/workflows/test/badge.svg
   :target: https://github.com/bckohan/django-typer/actions/workflows/test.yml

.. |Lint Status| image:: https://github.com/bckohan/django-typer/workflows/lint/badge.svg
   :target: https://github.com/bckohan/django-typer/actions/workflows/lint.yml

.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. _powershell: https://learn.microsoft.com/en-us/powershell/scripting/overview
.. _fish: https://fishshell.com/
.. _zsh: https://www.zsh.org/
.. _bash: https://www.gnu.org/software/bash/
.. _Django: https://www.djangoproject.com/

django-typer
############

Use `Typer <https://typer.tiangolo.com/>`_ to define the CLI for your Django_ management commands. 
Provides a TyperCommand class that inherits from `BaseCommand <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand>`_
and allows typer-style annotated parameter types. All of the BaseCommand functionality is
preserved, so that TyperCommand can be a drop in replacement.

**django-typer makes it easy to:**

   * Define your command CLI interface in a clear, DRY and safe way using type hints
   * Create subcommand and group command hierarchies.
   * Use the full power of Typer's parameter types to validate and parse command line inputs.
   * Create beautiful and information dense help outputs.
   * Configure the rendering of exception stack traces using rich.
   * `Install shell tab-completion support <https://django-typer.readthedocs.io/en/latest/shell_completion.html>`_
     for TyperCommands and normal Django commands for bash_, zsh_, fish_ and powershell_.
   * `Create custom and portable shell tab-completions for your CLI parameters <https://django-typer.readthedocs.io/en/latest/shell_completion.html#defining-custom-completions>`_.
   * Refactor existing management commands into TyperCommands because TyperCommand is interface
     compatible with BaseCommand.

Please refer to the `full documentation <https://django-typer.readthedocs.io/>`_ for more information.

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/doc/source/_static/img/closepoll_example.gif
   :width: 100%
   :align: center

Installation
------------

1. Clone django-typer from GitHub or install a release off `PyPI <https://pypi.org/project/django-typer/>`_:

    .. code:: bash

        pip install django-typer

    `rich <https://rich.readthedocs.io/en/latest/>`_ is a powerful library for rich text and
    beautiful formatting in the terminal. It is not required, but highly recommended for the
    best experience:

    .. code:: bash

        pip install "django-typer[rich]"


2. Add ``django_typer`` to your ``INSTALLED_APPS`` setting:

    .. code:: python

        INSTALLED_APPS = [
            ...
            'django_typer',
        ]

   *You only need to install django_typer as an app if you want to use the shellcompletion command
   to enable tab-completion or if you would like django-typer to install `rich traceback rendering 
   <https://django-typer.readthedocs.io/en/latest/howto.html#configure-rich-stack-traces>`_
   for you - which it does by default if rich is also installed.*

Basic Example
-------------

For example TyperCommands can be a very simple drop in replacement for BaseCommands. All of the
documented features of
`BaseCommand <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand>`_
work!


.. code-block:: python

   from django_typer import TyperCommand


   class Command(TyperCommand):

      def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
         """
         A basic command that uses Typer
         """



.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/basic.svg
   :width: 100%
   :align: center


|

Multiple Subcommands Example
-----------------------------

Or commands with multiple subcommands can be defined:

.. code-block:: python

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


.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi.svg
   :width: 100%
   :align: center

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi_create.svg
   :width: 100%
   :align: center

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/multi_delete.svg
   :width: 100%
   :align: center

|


Grouping and Hierarchies Example
--------------------------------

Or more complex groups and subcommand hierarchies can be defined. For example this command
defines a group of commands called math, with subcommands divide and multiply. The group
has a common initializer that optionally sets a float precision value. We would invoke this
command like so:

.. code:: bash

    ./manage.py hierarchy math --precision 5 divide 10 2.1
    4.76190
    ./manage.py hierarchy math multiply 10 2
    20.00

Any number of groups and subcommands and subgroups of other groups can be defined allowing
for arbitrarily complex command hierarchies.

.. code-block:: python

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


.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy.svg
   :width: 100%
   :align: center

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math.svg
   :width: 100%
   :align: center

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math_multiply.svg
   :width: 100%
   :align: center

.. image:: https://raw.githubusercontent.com/bckohan/django-typer/main/django_typer/examples/helps/hierarchy_math_divide.svg
   :width: 100%
   :align: center

|
