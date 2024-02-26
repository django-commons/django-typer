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
   :exclude-members: TyperCommand, Context
   :show-inheritance:

.. autoclass:: django_typer.TyperCommand

.. autoclass:: django_typer.TyperCommandMeta

.. autoclass:: django_typer.GroupFunction
    :members: group, command


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
    :members: traceback_config, get_current_command

.. _shellcompletion:

shellcompletion
---------------

.. automodule:: django_typer.management.commands.shellcompletion
    :members:
