.. include:: ./refs.rst
.. role:: big

============
Django Typer
============

Use Typer_ to define the CLI for your Django_ management commands using the typer interface.
Optionally use the provided TyperCommand class that inherits from BaseCommand_. This class maps
the typer interface onto a class based interface that Django developers will be familiar with.
All of the BaseCommand functionality is preserved, so that TyperCommand can be a drop in
replacement.

**django-typer makes it easy to:**

    * Define your command CLI interface in a clear, DRY and safe way using type hints
    * Create subcommand and group command hierarchies.
    * Use the full power of Typer's parameter types to validate and parse command line inputs.
    * Create beautiful and information dense help outputs.
    * Configure the rendering of exception stack traces using rich.
    * :ref:`Install shell tab-completion support <shellcompletions>` for TyperCommands and normal
      Django_ commands for bash_, zsh_, fish_ and powershell_.
    * :ref:`Create custom and portable shell tab-completions for your CLI parameters.
      <define-shellcompletions>`
    * Refactor existing management commands into TyperCommands because TyperCommand is interface
      compatible with BaseCommand.
    * Use either a class-based interface or the basic Typer style interface to define commands.


:big:`Installation`

1. Clone django-typer from GitHub_ or install a release off PyPI_ :

    .. code:: bash

        pip install django-typer

    rich_ is a powerful library for rich text and beautiful formatting in the terminal.
    It is not required, but highly recommended for the best experience:

    .. code:: bash

        pip install "django-typer[rich]"


2. Add ``django_typer`` to your ``INSTALLED_APPS`` setting:

    .. code:: python

        INSTALLED_APPS = [
            ...
            'django_typer',
        ]

   *You only need to install django_typer as an app if you want to use the shellcompletion command
   to enable tab-completion or if you would like django-typer to install*
   :ref:`rich traceback rendering <configure-rich-exception-tracebacks>` *for you - which it does by
   default if rich is also installed.*

:big:`Basic Example`

For example TyperCommands can be a very simple drop in replacement for BaseCommands. All of the
documented features of BaseCommand_ work!


.. literalinclude:: ../../django_typer/tests/apps/examples/basic/management/commands/basic.py
   :language: python
   :caption: A Basic Command
   :linenos:

Or, you may also use an interface identitical to Typer's. Simply import Typer from django_typer
instead of typer:

.. literalinclude:: ../../django_typer/tests/apps/examples/typer/management/commands/basic.py
   :language: python
   :caption: A Typer-style Basic Command
   :linenos:


.. typer:: django_typer.tests.apps.examples.basic.management.commands.basic.Command:typer_app
    :prog: ./manage.py basic
    :width: 80
    :convert-png: latex

|

:big:`Multiple Subcommands Example`

Commands with multiple subcommands can be defined:

.. literalinclude:: ../../django_typer/tests/apps/examples/basic/management/commands/multi.py
   :language: python
   :caption: A Command w/Subcommands
   :linenos:

Or using the typer-style interface this could be written:

.. literalinclude:: ../../django_typer/tests/apps/examples/typer/management/commands/multi.py
   :language: python
   :caption: A Typer-style Command w/Subcommands
   :linenos:


.. typer:: django_typer.tests.apps.examples.basic.management.commands.multi.Command:typer_app
    :prog: ./manage.py multi
    :width: 80
    :show-nested:
    :convert-png: latex

|


:big:`Grouping and Hierarchies Example`

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
for arbitrarily complex command hierarchies. Using the class-based interface we could define
the command like this:

.. literalinclude:: ../../django_typer/tests/apps/examples/basic/management/commands/hierarchy.py
   :language: python
   :caption: A Command w/Grouping Hierarchy
   :linenos:

The typer-style interface builds a TyperCommand class for us. This allows you to optionally
accept the self argument in your commands. We could define the above command using the typer
interface like this:

.. literalinclude:: ../../django_typer/tests/apps/examples/typer/management/commands/hierarchy.py
   :language: python
   :caption: A Typer-style Command w/Grouping Hierarchy
   :linenos:

.. typer:: django_typer.tests.apps.examples.basic.management.commands.hierarchy.Command:typer_app
    :prog: ./manage.py hierarchy
    :width: 80
    :show-nested:
    :convert-png: latex

|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   extensions
   howto
   shell_completion
   reference
   changelog
