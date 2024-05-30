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
:func:`~django_typer.command` or :func:`~django_typer.Typer.command`:

.. tabs::

    .. tab:: Django-style

        .. code-block:: python

            from django_typer import TyperCommand, command

            class Command(TyperCommand):

                @command()
                def subcommand1(self):
                    ...

                @command()
                def subcommand2(self):
                    ...

    .. tab:: Typer-style

        .. code-block:: python

            from django_typer import Typer

            app = Typer()

            @app.command()
            def subcommand1():
                ...

            @app.command()
            def subcommand2():
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


.. tabs::

    .. tab:: Django-style

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

    .. tab:: Typer-style

        .. code-block:: python

            from django_typer import Typer

            app = Typer()

            @app.command(name='subcommand1')
            def handle():
                ...

            @app.command()
            def subcommand2():
                ...

            @app.command()
            def subcommand3():
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

.. typer:: django_typer.tests.apps.test_app.management.commands.howto2.Command:typer_app
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


Use the Typer-like Interface
----------------------------

It may be more comfortable for developers familiar with Typer_ to use the function based interface
they are familiar with from Typer_. This is possible using django-typer simply by changing the
Typer import:

.. code-block:: python

    from django_typer import Typer  # do this instead of from typer import Typer

    app = Typer()  # this will install a Command class into this module

    @app.command()
    def main(name: str):
        ...

    # we can add groups by creating additional Typer apps just as you would in Typer
    def app2_init():
        # this is a typer callback() or initializer in django-typer parlance

    app2 = Typer(callback=app2_init)

    @app2.command()
    def app2_cmd(self):
        # the self argument is optional and supported on all decorated functions
        # in django-typer even in the Typer-like interface. Behind the scenes a
        # Command class is created and when invoked so to an instance, so we always
        # have the option of accepting self

    app.add_typer(app2)  # do not forget to attach the subgroup!


.. note::

    Decorated command functions that do not accept self are treated as staticmethods.


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


The rule of thumb is this:

    - Use call_command_ if your options and arguments need parsing.
    - Use :func:`~django_typer.get_command` and invoke the command functions directly if your
      options and arguments are already of the correct type.

If the second argument is a type, static type checking will assume the return value of get_command
to be of that type:

.. code-block:: python

    from django_typer import get_command
    from myapp.management.commands.math import Command as Math

    math = get_command("math", Math)
    math.add(10, 5)  # type checkers will resolve add parameters correctly

You may also fetch a subcommand function directly by passing its path:

.. code-block:: python

    get_command("math", "add")(10, 5)

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


Define Shell Tab Completions for Parameters
-------------------------------------------

See the section on :ref:`defining shell completions.<define-shellcompletions>`


Debug Shell Tab Completers
--------------------------

See the section on :ref:`debugging shell completers.<debug-shellcompletions>`


Extend/Override TyperCommands
-----------------------------

You can extend typer commands simply by subclassing them. All of the normal inheritance rules
apply. You can either subclass an existing command from an upstream app and leave its module the
same name to override the command or you can subclass and rename the module to provide an adapted
version of the upstream command with a different name. For example:

Say we have a command that looks like:

.. code-block:: python
    :caption: my_app/management/commands/my_cmd.py

    from django_Typer import TyperCommand, initialize, command, group

    class Command(TyperCommand):

        @initialize()
        def init(self):
            ...

        @command()
        def sub1(self):
            ...

        @command()
        def sub2(self):
            ...

        @group()
        def grp1(self):
            ...

        @grp1.command()
        def grp1_cmd1(self):
            ...


We can inherit and override or add additional commands and groups like so:

.. code-block:: python
    :caption: other_app/management/commands/ext_cmd.py

    from my_app.management.commands.my_cmd import Command as MyCMD
    from django_Typer import TyperCommand, initialize, command

    class Command(MyCMD):

        # override init
        @initialize()
        def init(self):
            ...

        # override sub1
        @command()
        def sub1(self):
            ...

        # add a 3rd top level command
        @command()
        def sub3(self):
            ...

        # add a new subcommand to grp1
        @MyCMD.grp1.command()
        def grp1_cmd2(self):
            ...


Notice that if we are adding to a group from the parent class, we have to use the group directly
(i.e. @ParentClass.group_name). Since we named our command ext_cmd it does not override my_cmd.
my_cmd is not affected and may be invoked in the same way as if ext_cmd was not present.

.. note::

    For more information on extension patterns see the tutorial on
    :ref:`Extending Commands <extensions>`.


Add to Existing TyperCommands
-----------------------------

You may add additional subcommands and command groups to existing commands by using django-typer_'s
extension pattern. This allows apps that do not know anything about each other to attach additional
CLI behavior to an upstream command and can be convenient for grouping loosely related behavior
into a single namespace (parent command).

To use our example from above, lets add and override the same behavior of my_cmd we did in ext_cmd
using this pattern instead:

First in other_app we need to create a new package under management. It can be called anything, but
for clarity lets call it extensions:

.. code-block:: text

    site/
    ├── my_app/
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── management/
    │   │   ├── __init__.py
    │   │   └── commands/
    │   │       ├── __init__.py
    │   │       └── my_cmd.py
    └── other_app/
        ├── __init__.py
        ├── apps.py
        └── management/
            ├── __init__.py
            ├── extensions/
            │   ├── __init__.py
            │   └── my_cmd.py <---- put your additive extensions to my_cmd here
            └── commands/
                └── __init__.py

Now we need to make sure our extensions are loaded. We do this by using the provided
:func:`~django_typer.utils.register_command_extensions` convenience function in
our app's ready() method:

.. code-block:: python
    :caption: other_app/apps.py

    from django.apps import AppConfig
    from django_typer.utils import register_command_extensions


    class MyAppConfig(AppConfig):
        name = "myapp"

        def ready(self):
            from .management import extensions

            register_command_extensions(extensions)


Now we can add extensions:


.. code-block:: python
    :caption: other_app/management/extensions/my_cmd.py

    from my_app.management.commands.my_cmd import Command as MyCMD

    # override init
    @MyCMD.initialize()
    def init(self):
        ...

    # override sub1
    @MyCMD.command()
    def sub1(self):
        ...

    # add a 3rd top level command
    @MyCMD.command()
    def sub3():  # self is always optional!
        ...

    # add a new subcommand to grp1
    @MyCMD.grp1.command()
    def grp1_cmd2(self):
        ...

The main difference here from normal inheritance is that we do not declare a new class, instead we
use the classmethod decorators on the class of the command we are extending. These extension
functions will also be added to the class. The self argument is always optional in django-typer_
and if it is not provided the function will be treated as a
`staticmethod <https://docs.python.org/3/library/functions.html#staticmethod>`_.

.. note::

    **Conflicting extensions are resolved in INSTALLED_APPS order.** For a detailed discussion
    about the utility of this pattern, see the tutorial on :ref:`Extending Commands <extensions>`.

.. warning::

    Take care not to import any extension code during or before Django's bootstrap procedure. This
    may result in conflict override behavior that does not honor INSTALLED_APPS order.

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
            """
            5: Command class docstrings are the last resort for
               the upper level command help string.
            """

            help = _("3")

            # if an initializer is present it's help will be used for the command level help

            @command(help=_("1"))
            def handle(self):
                """
                4: Function docstring is last priority and is not subject to translation.
                """

The rule for how helps are resolved when inheriting from other commands is that higher precedence
helps in base classes will be chosen over lower priority helps in deriving classes. However, if
you would like to use a docstring as the help in a derived class instead of the high priority
help in a base class you can set the equivalent priority help in the deriving class to a falsy
value:

.. code-block:: python

    class Command(TyperCommand, help=_("High precedence help defined in base class.")):
        ...

    ...

    from upstream.management.commands.command import Command as BaseCommand
    class Command(BaseCommand, help=None):
        """
        Docstring will be used as help.
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

You'll also need to make sure that Django is bootstrapped in your conf.py file:

.. code-block:: python
    :caption: conf.py

    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'path.to.your.settings')
    django.setup()


print, self.stdout and typer.echo
---------------------------------

There are no unbreakable rules about how you should print output from your commands.
You could use loggers, normal print statements or the BaseCommand_ stdout and
stderr output wrappers. Django advises the use of ``self.stdout.write`` because the
stdout and stderr streams can be configured by calls to call_command_ or
:func:`~django_tyoer.get_command` which allows you to easily grab output from your
commands for testing. Using the command's configured stdout and stderr
output wrappers also means output will respect the ``--force-color`` and ``--no-color``
parameters.

Typer_ and click_ provide `echo and secho <https://typer.tiangolo.com/tutorial/printing/>`_
functions that automatically handle byte to string conversions and offer simple styling
support. :class:`~django_typer.TyperCommand` provides :func:`~django_typer.TyperCommand.echo` and
:func:`~django_typer.TyperCommand.secho` wrapper functions for the Typer_ echo/secho
functions. If you wish to use Typer_'s echo you should use these wrapper functions because
they honor the command's ``--force-color`` and ``--no-color`` flags and the configured stdout/stderr
streams:

.. code-block:: python

    import typer
    from django_typer import TyperCommand

    class Command(TyperCommand):

        def handle(self):
            self.secho('Success!', fg=typer.colors.GREEN)


.. _howto-typer-style:

Adjust BaseCommand Parameters with a Typer-like Definition
-----------------------------------------------------------

You should probably just use the class-based interface! It is more natural
if you need to interface with BaseCommand_ features. But if you insist or
you just can't be bothered to convert an existing command here's how:

.. code-block:: python
    :caption: my_app/management/commands/my_command.py

    from django_typer import Typer, TyperCommand

    Command: TyperCommand  # use a type hint to give your IDE some autocomplete ideas!

    app = Typer()  # this will install a Command class into this module

    # Now you can just make adjustments directly to that Command class:
    # (safe to use Command after first Typer() call)
    Command.suppressed_base_arguments = {"--skip-checks", "--traceback", "--force-color"}

    @app.command()
    def main(name: str):
        ...


Extend Commands defined in the Typer-style
------------------------------------------

Commands that were defined using the Typer_ style interface generate Command classes that are
identical to the command if it were defined using :class:`~django_typer.TyperCommand`. Therefore
they can be inherited from just like commands defined using the class-based interface!

For example to extend the command from the :ref:`how-to above <howto-typer-style>`.

.. code-block:: python
    :caption: other_app/management/commands/my_command.py

    from my_app.management.commands.my_command import Command as MyCommand

    class Command(MyCommand):

        # all extension features work the same way as if MyCommand had been defined
        # using the class-based interface
        ...
