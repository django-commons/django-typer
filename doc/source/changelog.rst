==========
Change Log
==========

v2.2.0 (26-JUL-2024)
====================

* Implemented `ModelObjectCompleter should optionally accept a QuerySet in place of a Model class. <https://github.com/bckohan/django-typer/issues/96>`_

v2.1.3 (15-JUL-2024)
====================

* Fixed `Move from django_typer to django_typer.management broke doc reference links. <https://github.com/bckohan/django-typer/issues/98>`_
* Implemented `Support Django 5.1 <https://github.com/bckohan/django-typer/issues/97>`_

v2.1.2 (07-JUN-2024)
====================

* Fixed `Type hint kwargs to silence pylance warnings about partially unknown types <https://github.com/bckohan/django-typer/issues/93>`_

v2.1.1 (06-JUN-2024)
====================

* Fixed `handle = None does not work for mypy to silence type checkers <https://github.com/bckohan/django-typer/issues/90>`_

v2.1.0 (05-JUN-2024)
====================

.. warning::

    **Imports from** ``django_typer`` **have been deprecated and will be removed in 3.0!** Imports
    have moved to ``django_typer.management``:

    .. code-block::

        # old way
        from django_typer import TyperCommand, command, group, initialize, Typer

        # new way!
        from django_typer.management import TyperCommand, command, group, initialize, Typer

* Implemented `Only attempt to import rich and typer if settings has not disabled tracebacks. <https://github.com/bckohan/django-typer/issues/88>`_
* Implemented `Move tests into top level dir. <https://github.com/bckohan/django-typer/issues/87>`_
* Implemented `Move core code out of __init__.py into management/__init__.py <https://github.com/bckohan/django-typer/issues/81>`_
* Fixed `Typer(help="") doesnt work. <https://github.com/bckohan/django-typer/issues/78>`_

v2.0.2 (03-JUN-2024)
====================

* Fixed `class help attribute should be type hinted to allow a lazy translation string. <https://github.com/bckohan/django-typer/issues/85>`_


v2.0.1 (31-MAY-2024)
====================

* Fixed `Readme images are broken. <https://github.com/bckohan/django-typer/issues/77>`_

v2.0.0 (31-MAY-2024)
====================

This major version release, includes an extensive internal refactor, numerous bug fixes and the
addition of a plugin-based extension pattern.

* Fixed `Stack trace produced when attempted to tab-complete a non-existent management command. <https://github.com/bckohan/django-typer/issues/75>`_
* Fixed `Overriding handle() in inherited commands results in multiple commands. <https://github.com/bckohan/django-typer/issues/74>`_
* Implemented `Support subgroup name overloads. <https://github.com/bckohan/django-typer/issues/70>`_
* Fixed `Helps from class docstrings and TyperCommand class parameters are not inherited. <https://github.com/bckohan/django-typer/issues/69>`_
* Implemented `Allow callback and initialize to be aliases of each other. <https://github.com/bckohan/django-typer/issues/66>`_
* Implemented `Shell completion for --pythonpath <https://github.com/bckohan/django-typer/issues/65>`_
* Implemented `Shell completion for --settings <https://github.com/bckohan/django-typer/issues/64>`_
* Fixed `An intelligible exception should be thrown when a command is invoked that has no implementation. <https://github.com/bckohan/django-typer/issues/63>`_
* Implemented `TyperCommand class docstring should be used as the help as a last resort. <https://github.com/bckohan/django-typer/issues/62>`_
* Implemented `Adapter pattern that allows commands and groups to be added without extension by apps further up the app stack. <https://github.com/bckohan/django-typer/issues/61>`_
* Fixed `ModelObjectParser should use a metavar appropriate to the field type. <https://github.com/bckohan/django-typer/issues/60>`_
* Implemented `Switch to ruff for linting and formatting. <https://github.com/bckohan/django-typer/issues/56>`_
* Implemented `Add a wrapper for typer's echo/secho <https://github.com/bckohan/django-typer/issues/55>`_
* Implemented `Support a native typer-like interface. <https://github.com/bckohan/django-typer/issues/53>`_
* Fixed `@group type hint does not carry over the parameter spec of the wrapped function <https://github.com/bckohan/django-typer/issues/38>`_
* Implemented `Better test organization. <https://github.com/bckohan/django-typer/issues/34>`_
* Implemented `Add completer/parser for GenericIPAddressField. <https://github.com/bckohan/django-typer/issues/12>`_


v1.1.2 (22-APR-2024)
====================

* Fixed `Overridden common Django arguments fail to pass through when passed through call_command <https://github.com/bckohan/django-typer/issues/54>`_

v1.1.1 (11-APR-2024)
====================

* Implemented `Fix pyright type checking and add to CI <https://github.com/bckohan/django-typer/issues/51>`_
* Implemented `Convert CONTRIBUTING.rst to markdown <https://github.com/bckohan/django-typer/issues/50>`_

v1.1.0 (03-APR-2024)
====================

* Implemented `Convert readme to markdown. <https://github.com/bckohan/django-typer/issues/48>`_
* Fixed `typer 0.12.0 breaks django_typer 1.0.9 <https://github.com/bckohan/django-typer/issues/47>`_


v1.0.9 (yanked)
===============

* Fixed `Support typer 0.12.0 <https://github.com/bckohan/django-typer/issues/46>`_

v1.0.8 (26-MAR-2024)
====================

* Fixed `Support typer 0.10 and 0.11 <https://github.com/bckohan/django-typer/issues/45>`_

v1.0.7 (17-MAR-2024)
====================

* Fixed `Helps throw an exception when invoked from an absolute path that is not relative to the getcwd() <https://github.com/bckohan/django-typer/issues/44>`_

v1.0.6 (14-MAR-2024)
====================

* Fixed `prompt options on groups still prompt when given as named parameters on call_command <https://github.com/bckohan/django-typer/issues/43>`_


v1.0.5 (14-MAR-2024)
====================

* Fixed `Options with prompt=True are prompted twice <https://github.com/bckohan/django-typer/issues/42>`_


v1.0.4 (13-MAR-2024)
====================

* Fixed `Help sometimes shows full script path in Usage: when it shouldnt. <https://github.com/bckohan/django-typer/issues/40>`_
* Fixed `METAVAR when ModelObjectParser supplied should default to model name <https://github.com/bckohan/django-typer/issues/39>`_

v1.0.3 (08-MAR-2024)
====================

* Fixed `Incomplete typing info for @command decorator <https://github.com/bckohan/django-typer/issues/33>`_

v1.0.2 (05-MAR-2024)
====================

* Fixed `name property on TyperCommand is too generic and should be private. <https://github.com/bckohan/django-typer/issues/37>`_
* Fixed `When usage errors are thrown the help output should be that of the subcommand invoked not the parent group. <https://github.com/bckohan/django-typer/issues/36>`_
* Fixed `typer installs its own system exception hook when commands are run and this may step on the installed rich hook <https://github.com/bckohan/django-typer/issues/35>`_
* Fixed `Add py.typed stub <https://github.com/bckohan/django-typer/issues/31>`_
* Fixed `Run type checking with django-stubs installed. <https://github.com/bckohan/django-typer/issues/30>`_
* Fixed `Add pyright to linting and resolve any pyright errors. <https://github.com/bckohan/django-typer/issues/29>`_
* Fixed `Missing subcommand produces stack trace without --traceback. <https://github.com/bckohan/django-typer/issues/27>`_
* Fixed `Allow handle() to be an initializer. <https://github.com/bckohan/django-typer/issues/24>`_

v1.0.1 (29-FEB-2024)
====================

* Fixed `shell_completion broken for click < 8.1 <https://github.com/bckohan/django-typer/issues/21>`_

v1.0.0 (26-FEB-2024)
====================

* Initial production/stable release.

v0.6.1b (24-FEB-2024)
=====================

* Incremental beta release - this is also the second release candidate for version 1.
* Peg typer version to 0.9.x

v0.6.0b (23-FEB-2024)
=====================

* Incremental beta release - this is also the first release candidate for version 1.


v0.5.0b (31-JAN-2024)
=====================

* Incremental Beta Release

v0.4.0b (08-JAN-2024)
=====================

* Incremental Beta Release

v0.3.0b (06-JAN-2024)
=====================

* Incremental Beta Release

v0.2.0b (04-JAN-2024)
=====================

* Incremental Beta Release


v0.1.0b (05-DEC-2023)
=====================

* Initial Release (Beta)
