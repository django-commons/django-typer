.. include:: ./refs.rst

==========
Change Log
==========

v3.0.0 (202X-XX-XX)
===================

* BREAKING `Remove name parameter from initialize()/callback(). <https://github.com/django-commons/django-typer/issues/150>`_
* Implemented `Run full test suite on mac osx <https://github.com/django-commons/django-typer/issues/148>`_
* Implemented `Convert check.sh to justfile <https://github.com/django-commons/django-typer/issues/147>`_
* Implemented `Run full test suite on windows in CI <https://github.com/django-commons/django-typer/issues/146>`_
* Implemented `ANSI color control sequences should optionally be scrubbed from shell completions <https://github.com/django-commons/django-typer/issues/144>`_
* Fixed `supressed_base_arguments are still present in the Context <https://github.com/django-commons/django-typer/issues/143>`_
* Implemented `Add showcase of commands using django-typer to docs <https://github.com/django-commons/django-typer/issues/142>`_
* Implemented `Add a @finalize decorator for functions to collect/operate on subroutine results. <https://github.com/django-commons/django-typer/issues/140>`_
* Fixed `Remove management imports in django_typer/__init__.py <https://github.com/django-commons/django-typer/issues/95>`_
* Fixed `ParamSpec includes self for group methods <https://github.com/django-commons/django-typer/issues/73>`_
* Fixed `shellcompletion complete should print to the command's stdout. <https://github.com/django-commons/django-typer/issues/19>`_

Migrating from 2.x to 3.x
-------------------------

* The `name` parameter has been removed from
  :func:`django_typer.management.initialize()` and :func:`django_typer.management.Typer.callback()`.
  This change was forced by [upstream changes](https://github.com/fastapi/typer/pull/1052) in
  Typer_ that will allow :func:`django_typer.management.Typer.add_typer` to extend apps.
  
v2.6.0 (2024-12-03)
===================

* Fixed `On Python 3.13, sometimes flush is called on the stream wrapped by OutputWrapper after it is closed. <https://github.com/django-commons/django-typer/issues/155>`_
* Implemented `Support Typer 0.15.x <https://github.com/django-commons/django-typer/issues/154>`_

v2.5.0 (2024-11-29)
===================

* Implemented `Support Typer >=0.14 <https://github.com/django-commons/django-typer/issues/149>`_
* Fixed `Typer-style interface throws an assertion when no callback is present on a subgroup. <https://github.com/django-commons/django-typer/issues/145>`_

v2.4.0 (2024-11-07)
===================

* Implemented `Support Typer 0.13 <https://github.com/django-commons/django-typer/issues/138>`_

v2.3.0 (2024-10-13)
===================

* Fixed `Inheritance more than one level deep of TyperCommands does not work. <https://github.com/django-commons/django-typer/issues/131>`_
* Implemented `Drop python 3.8 support. <https://github.com/django-commons/django-typer/issues/130>`_
* Implemented `Command help order should respect definition order for class based commands. <https://github.com/django-commons/django-typer/issues/129>`_
* Fixed `Overriding the command group class does not work. <https://github.com/django-commons/django-typer/issues/128>`_
* Completed `Add project to test PyPI <https://github.com/django-commons/django-typer/issues/126>`_
* Completed `Open up vulnerability reporting and add security policy. <https://github.com/django-commons/django-typer/issues/124>`_
* Completed `Add example of custom plugin logic to plugins tutorial. <https://github.com/django-commons/django-typer/issues/122>`_
* Completed `Move architecture in docs to ARCHITECTURE.md <https://github.com/django-commons/django-typer/issues/121>`_
* Completed `Transfer to django-commons <https://github.com/django-commons/django-typer/issues/117>`_
* Completed `Add howto for how to change the display order of commands in help. <https://github.com/django-commons/django-typer/issues/116>`_

v2.2.2 (2024-08-25)
====================

* Implemented `Support python 3.13 <https://github.com/django-commons/django-typer/issues/109>`_
* Fixed `typer > 0.12.5 toggles rich help renderings off by default <https://github.com/django-commons/django-typer/issues/108>`_

v2.2.1 (2024-08-17)
====================

* Fixed `Remove shell_complete monkey patch when upstream PR is merged. <https://github.com/django-commons/django-typer/issues/66>`_

v2.2.0 (2024-07-26)
====================

* Implemented `ModelObjectCompleter should optionally accept a QuerySet in place of a Model class. <https://github.com/django-commons/django-typer/issues/96>`_

v2.1.3 (2024-07-15)
====================

* Fixed `Move from django_typer to django_typer.management broke doc reference links. <https://github.com/django-commons/django-typer/issues/98>`_
* Implemented `Support Django 5.1 <https://github.com/django-commons/django-typer/issues/97>`_

v2.1.2 (2024-06-07)
====================

* Fixed `Type hint kwargs to silence pylance warnings about partially unknown types <https://github.com/django-commons/django-typer/issues/93>`_

v2.1.1 (2024-06-06)
====================

* Fixed `handle = None does not work for mypy to silence type checkers <https://github.com/django-commons/django-typer/issues/90>`_

v2.1.0 (2024-06-05)
====================

.. warning::

    **Imports from** ``django_typer`` **have been deprecated and will be removed in 3.0!** Imports
    have moved to ``django_typer.management``:

    .. code-block::

        # old way
        from django_typer import TyperCommand, command, group, initialize, Typer

        # new way!
        from django_typer.management import TyperCommand, command, group, initialize, Typer

* Implemented `Only attempt to import rich and typer if settings has not disabled tracebacks. <https://github.com/django-commons/django-typer/issues/88>`_
* Implemented `Move tests into top level dir. <https://github.com/django-commons/django-typer/issues/87>`_
* Implemented `Move core code out of __init__.py into management/__init__.py <https://github.com/django-commons/django-typer/issues/81>`_
* Fixed `Typer(help="") doesnt work. <https://github.com/django-commons/django-typer/issues/78>`_

v2.0.2 (2024-06-03)
====================

* Fixed `class help attribute should be type hinted to allow a lazy translation string. <https://github.com/django-commons/django-typer/issues/85>`_


v2.0.1 (2024-05-31)
====================

* Fixed `Readme images are broken. <https://github.com/django-commons/django-typer/issues/77>`_

v2.0.0 (2024-05-31)
====================

This major version release, includes an extensive internal refactor, numerous bug fixes and the
addition of a plugin-based extension pattern.

* Fixed `Stack trace produced when attempted to tab-complete a non-existent management command. <https://github.com/django-commons/django-typer/issues/75>`_
* Fixed `Overriding handle() in inherited commands results in multiple commands. <https://github.com/django-commons/django-typer/issues/74>`_
* Implemented `Support subgroup name overloads. <https://github.com/django-commons/django-typer/issues/70>`_
* Fixed `Helps from class docstrings and TyperCommand class parameters are not inherited. <https://github.com/django-commons/django-typer/issues/69>`_
* Implemented `Allow callback and initialize to be aliases of each other. <https://github.com/django-commons/django-typer/issues/66>`_
* Implemented `Shell completion for --pythonpath <https://github.com/django-commons/django-typer/issues/65>`_
* Implemented `Shell completion for --settings <https://github.com/django-commons/django-typer/issues/64>`_
* Fixed `An intelligible exception should be thrown when a command is invoked that has no implementation. <https://github.com/django-commons/django-typer/issues/63>`_
* Implemented `TyperCommand class docstring should be used as the help as a last resort. <https://github.com/django-commons/django-typer/issues/62>`_
* Implemented `Adapter pattern that allows commands and groups to be added without extension by apps further up the app stack. <https://github.com/django-commons/django-typer/issues/61>`_
* Fixed `ModelObjectParser should use a metavar appropriate to the field type. <https://github.com/django-commons/django-typer/issues/60>`_
* Implemented `Switch to ruff for linting and formatting. <https://github.com/django-commons/django-typer/issues/56>`_
* Implemented `Add a wrapper for typer's echo/secho <https://github.com/django-commons/django-typer/issues/55>`_
* Implemented `Support a native typer-like interface. <https://github.com/django-commons/django-typer/issues/53>`_
* Fixed `@group type hint does not carry over the parameter spec of the wrapped function <https://github.com/django-commons/django-typer/issues/38>`_
* Implemented `Better test organization. <https://github.com/django-commons/django-typer/issues/34>`_
* Implemented `Add completer/parser for GenericIPAddressField. <https://github.com/django-commons/django-typer/issues/12>`_


v1.1.2 (2024-04-22)
====================

* Fixed `Overridden common Django arguments fail to pass through when passed through call_command <https://github.com/django-commons/django-typer/issues/54>`_

v1.1.1 (2024-04-11)
====================

* Implemented `Fix pyright type checking and add to CI <https://github.com/django-commons/django-typer/issues/51>`_
* Implemented `Convert CONTRIBUTING.rst to markdown <https://github.com/django-commons/django-typer/issues/50>`_

v1.1.0 (2024-04-03)
====================

* Implemented `Convert readme to markdown. <https://github.com/django-commons/django-typer/issues/48>`_
* Fixed `typer 0.12.0 breaks django_typer 1.0.9 <https://github.com/django-commons/django-typer/issues/47>`_


v1.0.9 (yanked)
===============

* Fixed `Support typer 0.12.0 <https://github.com/django-commons/django-typer/issues/46>`_

v1.0.8 (2024-03-26)
====================

* Fixed `Support typer 0.10 and 0.11 <https://github.com/django-commons/django-typer/issues/45>`_

v1.0.7 (2024-03-17)
====================

* Fixed `Helps throw an exception when invoked from an absolute path that is not relative to the getcwd() <https://github.com/django-commons/django-typer/issues/44>`_

v1.0.6 (2024-03-14)
====================

* Fixed `prompt options on groups still prompt when given as named parameters on call_command <https://github.com/django-commons/django-typer/issues/43>`_


v1.0.5 (2024-03-14)
====================

* Fixed `Options with prompt=True are prompted twice <https://github.com/django-commons/django-typer/issues/42>`_


v1.0.4 (2024-03-13)
====================

* Fixed `Help sometimes shows full script path in Usage: when it shouldnt. <https://github.com/django-commons/django-typer/issues/40>`_
* Fixed `METAVAR when ModelObjectParser supplied should default to model name <https://github.com/django-commons/django-typer/issues/39>`_

v1.0.3 (2024-03-08)
====================

* Fixed `Incomplete typing info for @command decorator <https://github.com/django-commons/django-typer/issues/33>`_

v1.0.2 (2024-03-05)
====================

* Fixed `name property on TyperCommand is too generic and should be private. <https://github.com/django-commons/django-typer/issues/37>`_
* Fixed `When usage errors are thrown the help output should be that of the subcommand invoked not the parent group. <https://github.com/django-commons/django-typer/issues/36>`_
* Fixed `typer installs its own system exception hook when commands are run and this may step on the installed rich hook <https://github.com/django-commons/django-typer/issues/35>`_
* Fixed `Add py.typed stub <https://github.com/django-commons/django-typer/issues/31>`_
* Fixed `Run type checking with django-stubs installed. <https://github.com/django-commons/django-typer/issues/30>`_
* Fixed `Add pyright to linting and resolve any pyright errors. <https://github.com/django-commons/django-typer/issues/29>`_
* Fixed `Missing subcommand produces stack trace without --traceback. <https://github.com/django-commons/django-typer/issues/27>`_
* Fixed `Allow handle() to be an initializer. <https://github.com/django-commons/django-typer/issues/24>`_

v1.0.1 (2024-02-29)
====================

* Fixed `shell_completion broken for click < 8.1 <https://github.com/django-commons/django-typer/issues/21>`_

v1.0.0 (2024-02-26)
====================

* Initial production/stable release.

v0.6.1b (2024-02-24)
=====================

* Incremental beta release - this is also the second release candidate for version 1.
* Peg typer version to 0.9.x

v0.6.0b (2024-02-23)
=====================

* Incremental beta release - this is also the first release candidate for version 1.


v0.5.0b (2024-01-31)
=====================

* Incremental Beta Release

v0.4.0b (2024-01-08)
=====================

* Incremental Beta Release

v0.3.0b (2024-01-06)
=====================

* Incremental Beta Release

v0.2.0b (2024-01-04)
=====================

* Incremental Beta Release


v0.1.0b (2023-12-05)
=====================

* Initial Release (Beta)
