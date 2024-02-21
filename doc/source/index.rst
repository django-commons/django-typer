.. include:: ./refs.rst

============
Django Typer
============

Use Typer_ to define the CLI for your Django management commands. Provides a TyperCommand class
that inherits from BaseCommand_ and allows typer-style annotated parameter types. All of the
BaseCommand functionality is preserved, so that TyperCommand can be a drop in replacement.

**django-typer makes it easy to:**

   * Define your command CLI interface in as clear, DRY, and safely as possible using type hints
   * Create subcommand and group command hierarchies.
   * Use the full power of Typer's parameter types to validate and parse command line inputs.
   * Create beautiful and information dense help outputs.
   * Configure the rendering of exception stack traces using rich.
   * Install shell tab-completion support for TyperCommands and normal Django commands for bash,
     zsh, fish and powershell.
   * Create custom and portable shell tab-completions for your CLI parameters.
   * Refactor existing management commands into TyperCommands because TyperCommand is interface
     compatible with BaseCommand.


Installation
------------

1. Clone django-typer from GitHub_ or install a release off PyPI_ :

    .. code:: bash

        pip install django-typer

    `rich <https://rich.readthedocs.io/en/latest/>`_ is a powerful library for rich text and
    beautiful formatting in the terminal. It is not required, but highly recommended for the
    best experience:

    .. code:: bash

        pip install django-typer[rich]


2. Add ``django_typer`` to your ``INSTALLED_APPS`` setting:

    .. code:: python

        INSTALLED_APPS = [
            ...
            'django_typer',
        ]


Basic Example
-------------

For example TyperCommands can be a very simple drop in replacement for BaseCommands. All of the
documented features of BaseCommand_ work!


.. literalinclude:: ../../django_typer/examples/basic.py
   :language: python
   :caption: A Basic Command
   :linenos:


.. typer:: django_typer.examples.basic.Command:typer_app
    :prog: basic
    :width: 80
    :convert-png: latex

|

Multiple Subcommands Example
----------------------------

Or commands with multiple subcommands can be defined:

.. literalinclude:: ../../django_typer/examples/multi.py
   :language: python
   :caption: A Command w/Subcommands
   :linenos:


.. typer:: django_typer.examples.multi.Command:typer_app
    :prog: multi
    :width: 80
    :show-nested:
    :convert-png: latex

|


Grouping and Hierarchies Example
--------------------------------

Or more complex groups and subcommand hierarchies can be defined:

.. literalinclude:: ../../django_typer/examples/hierarchy.py
   :language: python
   :caption: A Command w/Grouping Hierarchy
   :linenos:


.. typer:: django_typer.examples.hierarchy.Command:typer_app
    :prog: hierarchy
    :width: 80
    :show-nested:
    :convert-png: latex

|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   howto
   shell_completion
   commands
   reference
   changelog
