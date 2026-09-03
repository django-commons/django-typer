"""
Typer_ and :doc:`click <click:shell-completion>` provide tab-completion hooks for individual
parameters. As with :mod:`~django_typer.parsers` custom completion logic can be
implemented for custom parameter types and added to the annotation of the parameter.
Previous versions of Typer_ supporting :doc:`click <click:quickstart>` 7 used the
autocompletion argument to provide completion logic, Typer_ still supports this, but
passing ``shell_complete`` to the annotation is the preferred way to do this.

This package provides some completer functions and classes that work with common Django_
types:

- **models**: Complete model object field strings using
  :class:`~django_typer.completers.model.ModelObjectCompleter`.
- **django apps**: Complete app labels or names using
  :func:`~django_typer.completers.apps.app_labels`.
- **commands**: Complete Django command names using
  :func:`~django_typer.completers.cmd.commands`.
- **databases**: Complete Django database names using
  :func:`~django_typer.completers.db.databases`.
- **import paths**: Complete python import paths using
  :func:`~django_typer.completers.path.import_paths`.
- **paths**: Complete file and directory paths using
  :func:`~django_typer.completers.path.paths`.
- **directories**: Complete directories using
  :func:`~django_typer.completers.path.directories`.
- **media paths**: Complete Django media paths using
  :func:`~django_typer.completers.path.media_paths`.
- **static paths**: Complete Django static paths using
  :func:`~django_typer.completers.path.static_paths`.
- **languages**: Complete Django language names using
  :func:`~django_typer.completers.settings.languages`.
- **settings**: Complete Django settings variable names using
  :func:`~django_typer.completers.settings.setting`.

Completer functions receive a ``Context``, a ``Parameter`` and the incomplete string
and return a list of ``CompletionItem`` objects. Typer_ vendors these Click_ types,
so import them from here rather than from Click_ or from Typer_'s private modules:

.. code-block:: python

    from django_typer.completers import CompletionItem, Context, Parameter
"""

import typing as t

from typer._click import Context as Context
from typer._click import Parameter as Parameter
from typer._click.core import ParameterSource
from typer._click.shell_completion import CompletionItem as CompletionItem

Completer = t.Callable[[Context, Parameter, str], list[CompletionItem]]

ItemTuple = t.Any | tuple[t.Any, t.Any]
Strings = (
    t.Sequence[ItemTuple]
    | t.KeysView[t.Any]
    | t.ValuesView[t.Any]
    | t.ItemsView[t.Any, t.Any]
    | t.Generator[ItemTuple, None, None]
)


def these_strings(
    strings: t.Callable[[], Strings] | Strings,
    allow_duplicates: bool = False,
):
    """
    Get a completer that provides completion logic that matches the allowed strings.

    :param strings: A sequence of allowed strings or a callable that generates a
        sequence of allowed strings. If the sequence contains 2-tuples the second
        element is used as the help text for the completion item.
    :param allow_duplicates: Whether or not to allow duplicate values. Defaults to
        False.
    :return: A completer function.
    """

    def complete(ctx: Context, param: Parameter, incomplete: str):
        present = []
        items = []
        if (
            not allow_duplicates
            and param.name
            and ctx.get_parameter_source(param.name) is not ParameterSource.DEFAULT
        ):
            present = [value for value in (ctx.params.get(param.name) or [])]

        for item in strings() if callable(strings) else strings:
            help = None
            if isinstance(item, tuple):
                item, help = str(item[0]), str(item[1])
            if item.startswith(incomplete) and item not in present:
                items.append(CompletionItem(item, help=help))
        return items

    return complete


def chain(
    completer: Completer,
    *completers: Completer,
    first_match: bool = False,
    allow_duplicates: bool = False,
):
    """
    Run through the given completers and return the items from the first one, or all
    of them if first_match is False.

    .. note::

        This function is also useful for filtering out previously supplied duplicate
        values for completers that do not natively support that:

        .. code-block:: python

            shell_complete=chain(
                complete_import_path,
                allow_duplicates=False
            )

    :param completer: The first completer to use (must be at least one!)
    :param completers: The completers to use
    :param first_match: If true, return only the matches from the first completer that
        finds completions. Default: False
    :param allow_duplicates: If False (default) remove completions from previously
        provided values.
    """

    def complete(ctx: Context, param: Parameter, incomplete: str):
        completions = []
        present = []
        if (
            not allow_duplicates
            and param.name
            and ctx.get_parameter_source(param.name) is not ParameterSource.DEFAULT
        ):
            present = [value for value in (ctx.params.get(param.name) or [])]
        for cmpltr in [completer, *completers]:
            completions.extend(cmpltr(ctx, param, incomplete))
            if first_match and completions:
                break

        # eliminate duplicates
        return list(
            {
                ci.value: ci
                for ci in completions
                if ci.value
                if ci.value not in present
            }.values()
        )

    return complete
