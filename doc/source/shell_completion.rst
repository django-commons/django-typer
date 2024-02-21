.. include:: ./refs.rst

.. _shellcompletions:

=================
Shell Completions
=================

Shell completions are helpful suggestions that are displayed when you press the
``<TAB>`` key while typing a command in a shell.  They are especially useful
when you are not sure about the exact name of a command, its options, its arguments
or the potential values of either.

Django has some support for bash completions, but it is not enabled by default and
left to the user to install.

django-typer_ augments the upstream functionality of Typer_ and Click_ to provide
both an easy way to define shell completions for your custom CLI options and arguments
as well as a way to install them in your shell.

.. note::

    django-typer_ supports shell completion installation for bash_, zsh_, fish_ and
    powershell_.


Installation
============

Each shell has its own mechanism for enabling completions and this is further exacerbated
by how different shells are installed and configured on different platforms. All shells
have the same basic process. Completion logic needs to be registered with the shell that will be
invoked when tabs are pressed for a specific command or script. To install tab completions
for django commands we need to register our completion logic for Django manage script with
the shell. This process has two phases:

1. Ensure that your shell is configured to support completions.
2. Use the :ref:`shellcompletion <shellcompletion-command>` command to install the completion
   hook for your Django manage script.


It can be frustrating to debug why completions are not working as expected. The goal of this 
guide is not to be an exhaustive list of how to enable completions for each supported shell on
all possible platforms, but rather to provide general guidance on how to enable completions for
the most common platforms and environments. If you encounter issues or have solutions, please 
`report them on our issues page <https://github.com/bckohan/django-typer>`_

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

After installing the package you will need to add some configuration to your ``.zshrc`` file. We have
had luck with the following:

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

django-typer_ comes with a management command called :ref:`shellcompletion <shellcompletion-command>`.
To install completions for your Django project simply run the install command:

.. code-block:: bash

    ./manage.py shellcompletion install

.. note::

    The manage script may be named differently in your project - this is fine. The only requirement
    is that you invoke the shellcompletion command in the same way you would invoke any commands you
    would like tab completions to work for.

The installation script should be able to automatically detect your shell and install the appropriate
scripts. If it is unable to do so you may force it to install for a specific shell by passing the
shell name as an argument. Refer to the :ref:`command help <shellcompletion-command>` for details.

**After installation you will probably need to restart your shell or source the appropriate rc file.**

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

When tab completion is requested for a command that is not a TyperCommand, django-typer_ will delegate
that request to Django's `autocomplete function <https://github.com/django/django/blob/main/django/core/management/__init__.py#L278>`_
as a fallback. This means that using django-typer_ to install completion scripts will enable completions
for Django BaseCommands in all supported shells.

However, if you are using a separate package to define custom tab completions for your commands you may
use the --fallback parameter to supply a separate fallback hook that will invoke the appropriate
completion function for your commands. If there are other popular completion libraries please consider
`letting us know or submitting a PR <https://github.com/bckohan/django-typer/issues>`_ to support these
libraries as a fallback out of the box.


*The long-term solution here should be that Django itself manages completion installation and provides
hooks for implementing libraries to provide completions for their own commands.*


.. _define-shellcompletions:

Defining Custom Completions
===========================

