.. include:: ./refs.rst

.. _shellcompletions:

===============================
Tutorial: Shell Tab-Completions
===============================

.. only:: html

    .. image:: /_static/img/closepoll_example.gif
        :align: center

.. only:: latex

    .. image:: /_static/img/closepoll_example.png
        :align: center

|

Shell completions are helpful suggestions that are displayed when you press the
``<TAB>`` key while typing a command in a shell.  They are especially useful
when you are not sure about the exact name of a command, its options, its arguments
or the potential values of either.

Django has some support for bash completions, but it is not enabled by default and
left to the user to install.

django-typer_ augments the upstream functionality of Typer_ and Click_ to provide
both an easy way to define shell completions for your custom CLI options and arguments
as well as a way to install them in your shell.

.. tip::

    django-typer_ supports shell completion installation for bash_, zsh_, fish_ and
    powershell_.


Installation
============

Each shell has its own mechanism for enabling completions and this is further complicated
by how different shells are installed and configured on different platforms. All shells
have the same basic process. Completion logic needs to be registered with the shell that will be
invoked when tabs are pressed for a specific command or script. To install tab completions
for django commands we need to register our completion logic for Django manage script with
the shell. This process has two phases:

1. Ensure that your shell is configured to support completions.
2. Use the :mod:`~django_typer.management.commands.shellcompletion` command to install the
   completion hook for your Django manage script. This usually entails adding a specifically
   named script to a certain directory or adding lines to an existing script. The
   :mod:`~django_typer.management.commands.shellcompletion` command will handle this for you.


The goal of this guide is not to be an exhaustive list of how to enable completions for each
supported shell on all possible platforms, but rather to provide general guidance on how to
enable completions for the most common platforms and environments. If you encounter issues
or have solutions, please `report them on our issues page <https://github.com/django-commons/django-typer/issues>`_

Windows
-------

powershell_ is now bundled with most modern versions of Windows. There should be no additional
installation steps necessary, but please refer to the Windows documentation if powershell_ is not
present on your system.

Linux
-----

bash_ is the default shell on most Linux distributions. Completions should be enabled by default.

OSX
---

zsh_ is currently the default shell on OSX. Unfortunately completions are not supported out
of the box. We recommend using
`homebrew to install the zsh-completions package <https://formulae.brew.sh/formula/zsh-completions>`_.

After installing the package you will need to add some configuration to your ``.zshrc`` file. We
have had luck with the following:

.. code-block:: bash

    zstyle ':completion:*' menu select

    if type brew &>/dev/null; then
        FPATH=~/.zfunc:$(brew --prefix)/share/zsh-completions:$FPATH

        autoload -Uz compinit
        compinit
    fi

    fpath+=~/.zfunc


Install the Completion Hook
---------------------------

django-typer_ comes with a management command called
:mod:`~django_typer.management.commands.shellcompletion`. To install completions for your Django_
project simply run the install command:

.. code-block:: bash

    ./manage.py shellcompletion install

.. note::

    The manage script may be named differently in your project - this is fine. The only requirement
    is that you invoke the shellcompletion command in the same way you would invoke any commands you
    would like tab completions to work for.

The installation script should be able to automatically detect your shell and install the
appropriate scripts. If it is unable to do so you may force it to install for a specific shell by
passing the shell name as an argument. Refer to the
:mod:`~django_typer.management.commands.shellcompletion` for details.

**After installation you will need to restart your shell or source the appropriate rc file.**

.. warning::

    In production environments it is recommended that your management script be installed as a command
    on your system path. This will produce the most reliable installation.


Enabling Completions in Development Environments
------------------------------------------------

Most shells work best when the manage script is installed as an executable on the system path. This
is not always the case, especially in development environments. In these scenarios completion
installation *should still work*, but you may need to always invoke the script from the same path.
Fish_ may not work at all in this mode.


Integrating with Other CLI Completion Libraries
-----------------------------------------------

When tab completion is requested for a command that is not a :class:`~django_typer.management.TyperCommand`,
django-typer_ will delegate that request to Django's
`autocomplete function <https://github.com/django/django/blob/main/django/core/management/__init__.py#L278>`_
as a fallback. This means that using django-typer_ to install completion scripts will enable
completions for Django BaseCommands in all supported shells.

However, if you are using a separate package to define custom tab completions for your commands
you may use the --fallback parameter to supply a separate fallback hook that will invoke the
appropriate completion function for your commands. If there are other popular completion libraries
please consider `letting us know or submitting a PR
<https://github.com/django-commons/django-typer/issues>`_ to support these libraries as a fallback out of
the box.


*The long-term solution here should be that Django itself manages completion installation and
provides hooks for implementing libraries to provide completions for their own commands.*


.. _define-shellcompletions:

Defining Custom Completions
===========================

To define custom completion logic for your arguments_ and options_ pass the ``shell_completion``
parameter in your type hint annotations. django-typer_ comes with a
:ref:`few provided completers <completers>` for common Django_ types. One of the provided completers
completes Django_ app labels and names. We might build a similar completer that only works for
Django_ app labels like this:

.. tabs::

    .. tab:: Django-style

        .. literalinclude:: ../../examples/completers/management/commands/app_labels.py
            :language: python
            :linenos:
            :caption: examples/completers/management/commands/app_labels.py

    .. tab:: Typer-style

        .. literalinclude:: ../../examples/completers/management/commands/app_labels_typer.py
            :language: python
            :linenos:
            :caption: examples/completers/management/commands/app_labels_typer.py

.. tip::

    See the :class:`~django_typer.completers.ModelObjectCompleter` for a completer that works
    for many Django_ model field types.


.. _debug-shellcompletions:

Debugging Tab Completers
========================

Debugging tab completion code can be tricky because when invoked in situ in the shell the completer
code is run as a subprocess and it's output is captured by the shell. This means you can't set a
breakpoint and enter into the debugger easily.

To help with this django-typer_ provides a debug mode that will enter into the tab-completion logic
flow. Use the :class:`shellcompletion <django_typer.management.commands.shellcompletion.Command>`
:func:`~django_typer.management.commands.shellcompletion.Command.complete` command, to pass the
command line string that you would like to debug. For example:

.. code-block:: bash

    ./manage.py shellcompletion complete "mycommand --"


Provided Completers
===================


Django Apps
-----------

* completer: :func:`~django_typer.completers.complete_app_label`
* parser: :func:`~django_typer.parsers.parse_app_label`

.. code-block:: python

    import typing as t
    import typer
    from django.apps import AppConfig
    from django_typer import completers, parsers

    ...

    def handle(
        self,
        django_app: t.Annotated[
            AppConfig,
            typer.Argument(
                parser=parsers.parse_app_label,
                shell_complete=completers.complete_app_label,
            ),
        ],
    )

Constant Strings
----------------
* completer: :func:`~django_typer.completers.these_strings`

.. code-block:: python

    import typing as t
    import typer
    from enum import StrEnum
    from django_typer.completers import these_strings

    ...

    class Shells(StrEnum):

        zsh = 'zsh',
        bash = 'bash'
        fish = 'fish',
        powershell = 'pswh'

    def handle(
        self,
        shell: t.Annotated[
            Shells,
            typer.Argument(
                shell_complete=these_strings(list(Shells)),
            ),
        ],
    )

Database Aliases
----------------

* completer: :func:`~django_typer.completers.databases`

.. code-block:: python

    import typing as t
    import typer
    from django_typer.completers import databases

    ...

    def handle(
        self,
        database: t.Annotated[
            str,
            typer.Argument(
                shell_complete=databases,
            ),
        ],
    )

Management Commands
-------------------

* completer: :func:`~django_typer.completers.commands`

.. code-block:: python

    import typing as t
    import typer
    from django_typer.completers import commands

    ...

    def handle(
        self,
        command: t.Annotated[
            str,
            typer.Argument(
                shell_complete=commands,
            ),
        ],
    )


Paths (Files & Directories)
---------------------------

* completer: :func:`~django_typer.completers.complete_path`

.. code-block:: python

    import typing as t
    import typer
    from pathlib import Path
    from django_typer.completers import complete_path

    ...

    def handle(
        self,
        path: t.Annotated[
            Path,
            typer.Argument(
                shell_complete=complete_path,
            ),
        ],
    )

Directories
-----------

* completer: :func:`~django_typer.completers.complete_directory`

.. code-block:: python

    import typing as t
    import typer
    from pathlib import Path
    from django_typer.completers import complete_directory

    ...

    def handle(
        self,
        directory: t.Annotated[
            Path,
            typer.Argument(
                shell_complete=complete_directory,
            ),
        ],
    )


Import Paths
------------

Complete python.import.paths - uses sys.path. This completer is used for --settings

* completer: :func:`~django_typer.completers.complete_import_path`

.. code-block:: python

    import typing as t
    import typer
    from django_typer.completers import complete_import_path

    ...

    def handle(
        self,
        import_path: t.Annotated[
            str,
            typer.Argument(
                shell_complete=complete_import_path,
            ),
        ],
    )

Model Objects
-------------

* completer: :class:`~django_typer.completers.ModelObjectCompleter`
* parser: :class:`~django_typer.parsers.ModelObjectParser`
* convenience: :func:`~django_typer.management.model_parser_completer`

This completer/parser pairing provides the ability to fetch a model object from one of its fields.
Most field types are supported. Additionally any other field can be set as the help text that some
shells support. Refer to the reference documentation and the
:ref:`polls tutorial <building_commands>` for more information.

.. warning::

    If the model table is large you'll want to make sure the completable field is indexed. When
    your users hit tab, they'll have to wait to the matching query to complete. The queries
    have been optimized to take advantage of indexes for each supported field type.

.. code-block:: python

    import typing as t
    import typer
    from django_typer.management import model_parser_completer

    ...

    def handle(
        self,
        obj: t.Annotated[
            ModelClass,
            typer.Argument(
                **model_parser_completer(
                    ModelClass,  # may also accept a QuerySet for pre-filtering
                    'field_name',  # the field that should be matched (defaults to id)
                    help_field='other_field'  # optionally provide some additional help text
                ),
                help=_("Fetch objects by their field_names.")
            ),
        ]
    ):
        ...


Completer Chains
----------------

Multiple completers can be chained together in a sequence. All completions can
be returned, or only the first completer that generates matches.

* completer: :func:`~django_typer.completers.chain`

.. code-block:: python

    import typing as t
    import typer
    from django_typer import completers

    ...

    def handle(
        self,
        command: t.Annotated[
            str,
            typer.Argument(
                # allow commands to be specified by name or import path
                shell_complete=completers.chain(
                    completers.complete_import_path,
                    completers.commands
                )
            ),
        ],
    )
