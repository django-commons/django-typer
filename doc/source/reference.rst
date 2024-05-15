.. include:: ./refs.rst

.. _reference:

=========
Reference
=========

.. _base:

django_typer
------------

.. automodule:: django_typer
   :members:
   :exclude-members: Typer, CommandGroup, TyperCommand, Context
   :show-inheritance:

.. autoclass:: django_typer.Typer
    :members: callback, initialize, command, add_typer

.. autoclass:: django_typer.TyperCommand
    :members: initialize, callback, command, group, echo, secho, print_help

.. autoclass:: django_typer.TyperCommandMeta

.. autoclass:: django_typer.CommandGroup
    :members: callback, initialize, group, command


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
    :members: traceback_config, get_current_command, register_command_extensions

.. _shellcompletion:

shellcompletion
---------------

.. automodule:: django_typer.management.commands.shellcompletion
    :members:
