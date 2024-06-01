.. include:: ./refs.rst

.. _reference:

=========
Reference
=========

.. include:: ./architecture.rst

.. _base:

django_typer
------------

.. automodule:: django_typer
   :members:
   :exclude-members: Typer, CommandGroup, TyperCommand, Context, CommandNode
   :show-inheritance:

.. autoclass:: django_typer.Typer
    :members: callback, initialize, command, group, add_typer

.. autoclass:: django_typer.TyperCommand
    :members: initialize, callback, command, group, echo, secho, print_help, get_subcommand

.. autoclass:: django_typer.CommandNode
    :members: name, click_command, context, children, get_command, print_help

.. autoclass:: django_typer.TyperCommandMeta

.. _types:

types
-----

.. automodule:: django_typer.types
    :members:


.. _parsers:

parsers
-------

.. automodule:: django_typer.parsers
    :members:

.. _completers:

completers
----------

.. automodule:: django_typer.completers
    :members:


utils
-----

.. automodule:: django_typer.utils
    :members: traceback_config, get_current_command, register_command_plugins, is_method

.. _shellcompletion:

shellcompletion
---------------

.. automodule:: django_typer.management.commands.shellcompletion
    :members:

