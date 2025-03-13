.. include:: ./refs.rst

.. _reference:

=========
Reference
=========

.. _base:

django_typer
------------

.. automodule:: django_typer

.. automodule:: django_typer.management
   :members:
   :exclude-members: Typer, CommandGroup, TyperCommand, Context, CommandNode
   :show-inheritance:

.. autoclass:: django_typer.management.Context
    :members:

.. autoclass:: django_typer.management.Typer
    :members:

.. autoclass:: django_typer.management.TyperCommand
    :members:
    :special-members: __call__

.. autoclass:: django_typer.management.TyperParser
    :members:

.. autoclass:: django_typer.management.CommandNode
    :members:

.. autoclass:: django_typer.management.TyperCommandMeta

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

.. automodule:: django_typer.parsers.apps
    :members:

.. automodule:: django_typer.parsers.model
    :members:

.. _completers:

completers
----------

.. automodule:: django_typer.completers
    :members:

.. automodule:: django_typer.completers.apps
    :members:

.. automodule:: django_typer.completers.cmd
    :members:

.. automodule:: django_typer.completers.db
    :members:

.. automodule:: django_typer.completers.model
    :members:

.. automodule:: django_typer.completers.path
    :members:

utils
-----

.. automodule:: django_typer.utils
    :members: model_parser_completer, traceback_config, get_current_command, register_command_plugins, is_method, parse_iso_duration, duration_iso_string

.. _shellcompletion:

shellcompletion
---------------

.. automodule:: django_typer.management.commands.shellcompletion
    :members:

shells
~~~~~~

.. autoclass:: django_typer.shells.bash.BashComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.zsh.ZshComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.powershell.PowerShellComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.powershell.PwshComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.fish.FishComplete
    :members: name, template, color, supports_scripts
