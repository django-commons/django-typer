.. include:: ./refs.rst

======
How-To
======

Define an Argument
------------------

Positional arguments on a command are treated as positional command line arguments by Typer_.
For example to define an integer positional argument we could simply do:

.. code-block::

    def handle(self, int_arg: int):
        ...

You will likely want to add additional meta information to your arguments for Typer_ to render
things like helps and usage strings.  You can do this by annotating the type hint with
the `typer.Argument` class:

.. code-block::

    import typing as t
    from typer import Argument

    # ...

    def handle(self, int_arg: t.Annotated[int, Argument(help="An integer argument")]):
        ...

.. tip::

    Refer to the Typer_ docs on arguments_ for more details.


Define an Option
----------------

Options are like arguments but are not position dependent and instead provided with a preceding
identifier string (e.g. `--name`).

When a default value is provided for a parameter, Typer_ will treat it as an option.  For example:

.. code-block:: python

    def handle(self, flag: bool = False):
        ...

Would be called like this:

.. code-block:: bash

    $ mycommand --flag

If the type hint on the option is something other than a boolean it will accept a value:

.. code-block:: bash

    def handle(self, name: str = "world"):
        ...

Would be called like this:

.. code-block:: bash

    $ mycommand --name=world
    $ mycommand --name world  # this also works

To add meta information, we annotate with the `typer.Option` class:

.. code-block::

    import typing as t
    from typer import Option

    # ...

    def handle(self, name: t.Annotated[str, Option(help="The name of the thing")]):
        ...

.. tip::

    Refer to the Typer_ docs on options_ for more details.


.. _multi_commands:

Define Multiple Subcommands
---------------------------

Commands with a single executable function should simply implement handle(), but if you would
like have multiple subcommands you can define any number of functions decorated with
:func:`~django_typer.command`:

.. code-block:: python

    from django_Typer import TyperCommand, command

    class Command(TyperCommand):

        @command()
        def subcommand1(self):
            ...

        @command()
        def subcommand2(self):
            ...

.. note::

    When no handle() method is defined, you cannot invoke a command instance as a callable. instead
    you should invoke subcommands directly:

    .. code-block:: python

        from django_typer import get_command

        command = get_command("mycommand")
        command.subcommand1()
        command.subcommand2()

        command() # this will raise an error


.. _multi_with_defaults:

Define Multiple Subcommands w/ a Default
-----------------------------------------

We can also implement a default subcommand by defining a handle() method, and we can rename it to
whatever we want the command to be. For example to define three subcommands but have one as the
default we can do this:


.. code-block:: python

    from django_typer import TyperCommand, command

    class Command(TyperCommand):

        @command(name='subcommand1')
        def handle(self):
            ...

        @command()
        def subcommand2(self):
            ...

        @command()
        def subcommand3(self):
            ...


.. code-block:: python

    from django_typer import get_command

    command = get_command("mycommand")
    command.subcommand2()
    command.subcommand3()

    command() # this will invoke handle (i.e. subcommand1)

    # note - we *cannot* do this:
    command.handle()

    # or this:
    command.subcommand1()


Lets look at the help output:

.. typer:: django_typer.tests.test_app.management.commands.howto2.Command:typer_app
    :width: 80


Define Groups of Commands
-------------------------

Any depth of command tree can be defined. Use the :func:`~django_typer.group` decorator to define
a group of subcommands:

.. code-block:: python

    from django_Typer import TyperCommand, command, group

    class Command(TyperCommand):

        @group()
        def group1(self, common_option: bool = False):
            # you can define common options that will be available to all subcommands of
            # the group, and implement common initialization logic here.

        @group()
        def group2(self):
            ...

        # attach subcommands to groups by using the command decorator on the group function
        @group1.command()
        def grp1_subcommand1(self):
            ...

        @group1.command()
        def grp1_subcommand1(self):
            ...

        # groups can have subgroups!
        @group1.group()
        def subgroup1(self):
            ...

        @subgroup1.command()
        def subgrp_command(self):
            ...


Define an Initialization Callback
---------------------------------

You can define an initializer function that takes arguments_ and options_ that will be invoked
before your handle() command or subcommands using the :func:`~django_typer.initialize` decorator.
This is like defining a group at the command root and is an extension of the
`typer callback mechanism <https://typer.tiangolo.com/tutorial/commands/callback/>`_.

.. code-block:: python

    from django_Typer import TyperCommand, initialize, command

    class Command(TyperCommand):

        @initialize()
        def init(self, common_option: bool = False):
            # you can define common options that will be available to all subcommands of
            # the command, and implement common initialization logic here. This will be
            # invoked before the chosen command
            ...

        @command()
        def subcommand1(self):
            ...

        @command()
        def subcommand2(self):
            ...


Call TyperCommands from Code
----------------------------

There are two options for invoking a :class:`~django_typer.TyperCommand` from code without spawning
off a subprocess. The first is to use Django_'s builtin call_command_ function. This function will
work exactly as it does for normal BaseCommand_ derived commands. django-typer_ however adds
another mechanism that can be more efficient, especially if your options and arguments are already
of the correct type and require no parsing:

Say we have this command, called ``mycommand``:

.. code-block:: python

    from django_typer import TyperCommand, command

    class Command(TyperCommand):

        def handle(self, count: int=5):
            return count


.. code-block:: python

    from django.core.management import call_command
    from django_typer import get_command

    # we can use use call_command like with any Django command
    call_command("mycommand", count=10)
    call_command("mycommand", '--count=10')  # this will work too

    # or we can use the get_command function to get the command instance and invoke it directly
    mycommand = get_command("mycommand")
    mycommand(count=10)
    mycommand(10) # this will work too

    # return values are also available
    assert mycommand(10) == 10


The rule of them is this:

    - Use call_command_ if your options and arguments need parsing.
    - Use :func:`~django_typer.get_command` and invoke the command functions directly if your
      options and arguments are already of the correct type.

.. tip::

    Also refer to the :func:`~django_typer.get_command` docs and :ref:`here <multi_with_defaults>`
    and :ref:`here <multi_commands>` for the nuances of calling commands when handle() is and is
    not implemented.

Change Default Django Options
-----------------------------

:class:`~django_typer.TyperCommand` classes preserve all of the functionality of BaseCommand_ derivatives.
This means that you can still use class members like `suppressed_base_arguments
<https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/#django.core.management.BaseCommand.suppressed_base_arguments>`_
to suppress default options.

By default :class:`~django_typer.TyperCommand` suppresses ``--verbosity``. You can add it back by
setting ``suppressed_base_arguments`` to an empty list. If you want to use verbosity you can
simply redefine it or use one of django-typer_'s :ref:`provided type hints <types>` for the default
BaseCommand_ options:

.. code-block:: python

    from django_typer import TyperCommand
    from django_typer.types import Verbosity

    class Command(TyperCommand):

        suppressed_base_arguments = ['--settings']  # remove the --settings option

        def handle(self, verbosity: Verbosity=1):
            ...


Configure the Typer_ Application
--------------------------------

Typer_ apps can be configured using a number of parameters. These parameters are usually passed
to the Typer class constructor when the application is created. django-typer_ provides a way to
pass these options upstream to Typer_ by supplying them as keyword arguments to the
:class:`~django_typer.TyperCommand` class inheritance:

.. code-block:: python

    from django_typer import TyperCommand

    class Command(TyperCommand, chain=True):
        # here we pass chain=True to typer telling it to allow invocation of
        # multiple subcommands
        ...


.. tip::

    See :class:`~django_typer.TyperCommandMeta` for a list of available parameters. Also refer to
    the `Typer docs <https://typer.tiangolo.com>`_ for more details. Note that not all of these
    parameters make sense in the context of a Django management command, so behavior for some
    is undefined.


Define Shell Completions for Parameter values
----------------------------------------------

See the section on :ref:`defining shell completions.<define-shellcompletions>`


.. _configure-rich-exception-tracebacks:

Configure rich_ Stack Traces
----------------------------

When rich_ is installed it may be `configured to display rendered stack traces
<https://rich.readthedocs.io/en/stable/traceback.html>`_ for unhandled exceptions.
These stack traces are information dense and can be very helpful for debugging. By default, if
rich_ is installed django-typer_ will configure it to render stack traces. You can disable
this behavior by setting the ``DT_RICH_TRACEBACK_CONFIG`` config to ``False``. You may also
set ``DT_RICH_TRACEBACK_CONFIG`` to a dictionary holding the parameters to pass to
`rich.traceback.install`.

This provides a common hook for configuring rich_ that you can control on a per-deployment basis:

.. code-block::
    :caption: settings.py

    # refer to the rich docs for details
    DT_RICH_TRACEBACK_CONFIG = {
        "console": rich.console.Console(), # create a custom Console object for rendering
        "width": 100,                      # default is 100
        "extra_lines": 3,                  # default is 3
        "theme": None,                     # predefined themes
        "word_wrap": False,                # default is False
        "show_locals": True,               # rich default is False, but we turn this on
        "locals_max_length":               # default is 10
        "locals_max_string":               # default is 80
        "locals_hide_dunder": True,        # default is True
        "locals_hide_sunder": False,       # default is None
        "indent_guides": True,             # default is True
        "suppress": [],                    # suppress frames from these module import paths
        "max_frames": 100                  # default is 100
    }

    # or turn off rich traceback rendering
    DT_RICH_TRACEBACK_CONFIG = False

.. tip::

    There are traceback configuration options that can be supplied as configuration parameters to
    the Typer_ application. It is best to not set these and allow users to configure tracebacks
    via the ``DT_RICH_TRACEBACK_CONFIG`` setting.

Add Help Text to Commands
-------------------------

There are multiple places to add help text to your commands. There is however a precedence order,
and while lazy translation is supported in help texts, if you use docstrings as the helps they will
not be translated.

The precedence order, for a simple command is as follows:

    .. code-block:: python

        from django_typer import TyperCommand, command
        from django.utils.translation import gettext_lazy as _

        class Command(TyperCommand, help=_('2')):

            help = _("3")

            @command(help=_("1"))
            def handle(self):
                """
                Docstring is last priority and is not subject to translation.
                """


Document Commands w/Sphinx
--------------------------

Checkout `this Sphinx extension <https://github.com/sphinx-contrib/typer>`_ that can be used to
render your rich helps to Sphinx docs.

For example, to document a :class:`~django_typer.TyperCommand` with sphinxcontrib-typer, you would
do something like this:

.. code-block:: rst

    .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app
        :prog: ./manage.py shellcompletion
        :show-nested:
        :width: 80

The Typer_ application object is a property of the command class and is named `typer_app`. The typer
directive simply needs to be given the fully qualified import path of the application object.

Or we could render the helps for individual subcommands as well:

.. code-block:: rst

    .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:install
        :prog: ./manage.py shellcompletion
        :width: 80
