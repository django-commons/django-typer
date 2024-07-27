"""
Typer_ and click_ provide tab-completion hooks for individual parameters. As with
:mod:`~django_typer.parsers` custom completion logic can be implemented for custom
parameter types and added to the annotation of the parameter. Previous versions of
Typer_ supporting click_ 7 used the autocompletion argument to provide completion
logic, Typer_ still supports this, but passing ``shell_complete`` to the annotation is
the preferred way to do this.

This module provides some completer functions and classes that work with common Django_
types:

- **Model Objects**: Complete model object field strings using :class:`ModelObjectCompleter`.
- **App Labels**: Complete app labels or names using :func:`complete_app_label`.

"""

# pylint: disable=line-too-long

import inspect
import os
import pkgutil
import sys
import typing as t
from functools import partial
from pathlib import Path
from types import MethodType
from uuid import UUID

from click import Context, Parameter
from click.core import ParameterSource
from click.shell_completion import CompletionItem
from django.apps import apps
from django.conf import settings
from django.core.management import get_commands
from django.db.models import (
    CharField,
    DecimalField,
    Field,
    FloatField,
    GenericIPAddressField,
    IntegerField,
    Manager,
    Max,
    Model,
    Q,
    TextField,
    UUIDField,
)
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _

Completer = t.Callable[[Context, Parameter, str], t.List[CompletionItem]]
Strings = t.Union[t.Sequence[str], t.KeysView[str], t.Generator[str, None, None]]


class ModelObjectCompleter:
    """
    A completer for generic Django model objects. This completer will work
    for most Django core model field types where completion makes sense.

    This completer currently supports the following field types and their subclasses:

        - `IntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield>`_
            - `AutoField <https://docs.djangoproject.com/en/stable/ref/models/fields/#autofield>`_
            - `BigAutoField <https://docs.djangoproject.com/en/stable/ref/models/fields/#bigautofield>`_
            - `BigIntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield>`_
            - `SmallIntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#smallintegerfield>`_
            - `PositiveIntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#positiveintegerfield>`_
            - `PositiveSmallIntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#positivesmallintegerfield>`_
            - `SmallAutoField <https://docs.djangoproject.com/en/stable/ref/models/fields/#smallautofield>`_
        - `CharField <https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield>`_
            - `SlugField <https://docs.djangoproject.com/en/stable/ref/models/fields/#slugfield>`_
            - `URLField <https://docs.djangoproject.com/en/stable/ref/models/fields/#urlfield>`_
            - `EmailField <https://docs.djangoproject.com/en/stable/ref/models/fields/#emailfield>`_
        - `TextField <https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield>`_
        - `UUIDField <https://docs.djangoproject.com/en/stable/ref/models/fields/#uuidfield>`_
        - `FloatField <https://docs.djangoproject.com/en/stable/ref/models/fields/#floatfield>`_
        - `DecimalField <https://docs.djangoproject.com/en/stable/ref/models/fields/#decimalfield>`_
        - `GenericIPAddressField <https://docs.djangoproject.com/en/stable/ref/models/fields/#genericipaddressfield>`_

    The completer query logic is pluggable, but the defaults cover most use cases. The
    limit field is important. It defaults to 50 meaning if more than 50 potential completions
    are found only the first 50 will be returned and there will be no indication to the user
    that there are more. This is to prevent the shell from becoming unresponsive when offering
    completion for large tables.

    To use this completer, pass an instance of this class to the `shell_complete`
    argument of a typer.Option or typer.Argument:

    .. code-block:: python

        from django_typer.completers import ModelObjectCompleter

        class Command(TyperCommand):

            def handle(
                self,
                model_obj: Annotated[
                    MyModel,
                    typer.Argument(
                        shell_complete=ModelObjectCompleter(MyModel, lookup_field="name"),
                        help=_("The model object to use.")
                    )
                ]
            ):
                ...

    .. note::

        See also :func:`~django_typer.model_parser_completer` for a convenience
        function that returns a configured parser and completer for a model object
        and helps reduce boilerplate.

    :param model_or_qry: The Django model class or a queryset to filter against.
    :param lookup_field: The name of the model field to use for lookup.
    :param help_field: The name of the model field to use for help text or None if
        no help text should be provided.
    :param query: A callable that accepts the completer object instance, the click
        context, the click parameter, and the incomplete string and returns a Q
        object to use for filtering the queryset. The default query will use the
        relevant class methods depending on the lookup field class. See the
        query methods for details.
    :param limit: The maximum number of completion items to return. If None, all
        matching items will be returned. When offering completion for large tables
        you'll want to set this to a reasonable limit. Default: 50
    :param case_insensitive: Whether or not to perform case insensitive matching when
        completing text-based fields. Defaults to False.
    :param distinct: Whether or not to filter out duplicate values. Defaults to True.
        This is not the same as calling distinct() on the queryset - which will happen
        regardless - but rather whether or not to filter out values that are already
        given for the parameter on the command line.
    """

    QueryBuilder = t.Callable[["ModelObjectCompleter", Context, Parameter, str], Q]

    model_cls: t.Type[Model]
    _queryset: t.Optional[QuerySet] = None
    lookup_field: str
    help_field: t.Optional[str] = None
    query: t.Callable[[Context, Parameter, str], Q]
    limit: t.Optional[int] = 50
    case_insensitive: bool = False
    distinct: bool = True

    # used to adjust the index into the completion strings when we concatenate
    # the incomplete string with the lookup field value - see UUID which has
    # to allow for - to be missing
    _offset: int = 0

    _field: Field

    @property
    def queryset(self) -> t.Union[QuerySet, Manager[Model]]:
        return self._queryset or self.model_cls.objects

    def to_str(self, obj: t.Any) -> str:
        return str(obj)

    def int_query(self, context: Context, parameter: Parameter, incomplete: str) -> Q:
        """
        The default completion query builder for integer fields. This method will
        return a Q object that will match any value that starts with the incomplete
        string. For example, if the incomplete string is "1", the query will match
        1, 10-19, 100-199, 1000-1999, etc.

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A Q object to use for filtering the queryset.
        :raises ValueError: If the incomplete string is not a valid integer.
        :raises TypeError: If the incomplete string is not a valid integer.
        """
        lower = int(incomplete)
        upper = lower + 1
        max_val = self.model_cls.objects.aggregate(Max(self.lookup_field))[
            f"{self.lookup_field}__max"
        ]
        qry = Q(**{f"{self.lookup_field}__gte": lower}) & Q(
            **{f"{self.lookup_field}__lt": upper}
        )
        while (lower := lower * 10) <= max_val:
            upper *= 10
            qry |= Q(**{f"{self.lookup_field}__gte": lower}) & Q(
                **{f"{self.lookup_field}__lt": upper}
            )
        return qry

    def float_query(self, context: Context, parameter: Parameter, incomplete: str) -> Q:
        """
        The default completion query builder for float fields. This method will
        return a Q object that will match any value that starts with the incomplete
        string. For example, if the incomplete string is "1.1", the query will match
        1.1 <= float(incomplete) < 1.2

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A Q object to use for filtering the queryset.
        :raises ValueError: If the incomplete string is not a valid float.
        :raises TypeError: If the incomplete string is not a valid float.
        """
        incomplete = incomplete.rstrip("0").rstrip(".")
        lower = float(incomplete)
        if "." in incomplete:
            upper = lower + float(f'0.{"0"*(len(incomplete)-incomplete.index(".")-2)}1')
        else:
            return self.int_query(context, parameter, incomplete)
        return Q(**{f"{self.lookup_field}__gte": lower}) & Q(
            **{f"{self.lookup_field}__lt": upper}
        )

    def text_query(self, context: Context, parameter: Parameter, incomplete: str) -> Q:
        """
        The default completion query builder for text-based fields. This method will
        return a Q object that will match any value that starts with the incomplete
        string. Case sensitivity is determined by the case_insensitive constructor parameter.

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A Q object to use for filtering the queryset.
        """
        if self.case_insensitive:
            return Q(**{f"{self.lookup_field}__istartswith": incomplete})
        return Q(**{f"{self.lookup_field}__startswith": incomplete})

    def uuid_query(self, context: Context, parameter: Parameter, incomplete: str) -> Q:
        """
        The default completion query builder for UUID fields. This method will
        return a Q object that will match any value that starts with the incomplete
        string. The incomplete string will be stripped of all non-alphanumeric
        characters and padded with zeros to 32 characters. For example, if the
        incomplete string is "a", the query will match
        a0000000-0000-0000-0000-000000000000 to affffffff-ffff-ffff-ffff-ffffffffffff.

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A Q object to use for filtering the queryset.
        :raises ValueError: If the incomplete string is too long or contains invalid
            UUID characters. Anything other than (0-9a-fA-F).
        """

        # the offset futzing is to allow users to ignore the - in the UUID
        # as a convenience of its implementation any non-alpha numeric character
        # will be ignored, and the completion suggestions and parsing will still work
        uuid = ""
        self._offset = 0
        for char in incomplete:
            if char.isalnum():
                uuid += char
            else:
                self._offset -= 1

        if len(incomplete) >= 9:
            self._offset += 1
        if len(incomplete) >= 14:
            self._offset += 1
        if len(incomplete) >= 19:
            self._offset += 1
        if len(incomplete) >= 24:
            self._offset += 1

        if len(uuid) > 32:
            raise ValueError(
                _("Too many UUID characters: {incomplete}").format(
                    incomplete=incomplete
                )
            )
        min_uuid = UUID(uuid + "0" * (32 - len(uuid)))
        max_uuid = UUID(uuid + "f" * (32 - len(uuid)))
        return Q(**{f"{self.lookup_field}__gte": min_uuid}) & Q(
            **{f"{self.lookup_field}__lte": max_uuid}
        )

    def __init__(
        self,
        model_or_qry: t.Union[t.Type[Model], QuerySet],
        lookup_field: t.Optional[str] = None,
        help_field: t.Optional[str] = help_field,
        query: t.Optional[QueryBuilder] = None,
        limit: t.Optional[int] = limit,
        case_insensitive: bool = case_insensitive,
        distinct: bool = distinct,
    ):
        if inspect.isclass(model_or_qry) and issubclass(model_or_qry, Model):
            self.model_cls = model_or_qry
        elif isinstance(model_or_qry, QuerySet):  # type: ignore
            self.model_cls = model_or_qry.model
            self._queryset = model_or_qry
        else:
            raise ValueError(
                _("ModelObjectCompleter requires a Django model class or queryset.")
            )
        self.lookup_field = str(
            lookup_field or getattr(self.model_cls._meta.pk, "name", "id")
        )
        self.help_field = help_field
        self.limit = limit
        self.case_insensitive = case_insensitive
        self.distinct = distinct

        self._field = self.model_cls._meta.get_field(  # pylint: disable=protected-access
            self.lookup_field
        )
        if query:
            self.query = MethodType(query, self)
        else:
            if isinstance(self._field, IntegerField):
                self.query = self.int_query
            elif isinstance(self._field, (CharField, TextField, GenericIPAddressField)):
                self.query = self.text_query
            elif isinstance(self._field, UUIDField):
                self.query = self.uuid_query
            elif isinstance(self._field, (FloatField, DecimalField)):
                self.query = self.float_query
            else:
                raise ValueError(
                    _("Unsupported lookup field class: {cls}").format(
                        cls=self._field.__class__.__name__
                    )
                )

    def __call__(
        self, context: Context, parameter: Parameter, incomplete: str
    ) -> t.Union[t.List[CompletionItem], t.List[str]]:
        """
        The completer method. This method will return a list of CompletionItem
        objects. If the help_field constructor parameter is not None, the help
        text will be set on the CompletionItem objects. The configured query
        method will be used to filter the queryset. distinct() will also be
        applied and if the distinct constructor parameter is True, values already
        present for the parameter on the command line will be filtered out.

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A list of CompletionItem objects.
        """

        completion_qry = Q()

        if incomplete:
            try:
                completion_qry &= self.query(  # pylint: disable=not-callable
                    context, parameter, incomplete
                )
            except (ValueError, TypeError):
                return []

        excluded: t.List[t.Type[Model]] = []
        if (
            self.distinct
            and parameter.name
            and context.get_parameter_source(parameter.name)
            is not ParameterSource.DEFAULT
        ):
            excluded = context.params.get(parameter.name, []) or []

        return [
            CompletionItem(
                # use the incomplete string prefix incase this was a case insensitive match
                value=incomplete
                + self.to_str(getattr(obj, self.lookup_field))[
                    len(incomplete) + self._offset :
                ],
                help=getattr(obj, self.help_field, None) if self.help_field else "",
            )
            for obj in self.queryset.filter(completion_qry).distinct()[0 : self.limit]
            if (
                getattr(obj, self.lookup_field) is not None
                and self.to_str(getattr(obj, self.lookup_field))
                and obj not in excluded
            )
        ]


def complete_app_label(
    ctx: Context, param: Parameter, incomplete: str
) -> t.List[CompletionItem]:
    """
    A case-sensitive completer for Django app labels or names. The completer
    prefers labels but names will also work.

    .. code-block:: python

        import typing as t
        import typer
        from django_typer.management import TyperCommand
        from django_typer.parsers import parse_app_label
        from django_typer.completers import complete_app_label

        class Command(TyperCommand):

            def handle(
                self,
                django_apps: t.Annotated[
                    t.List[AppConfig],
                    typer.Argument(
                        parser=parse_app_label,
                        shell_complete=complete_app_label,
                        help=_("One or more application labels.")
                    )
                ]
            ):
                ...

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :return: A list of matching app labels or names. Labels already present for the
        parameter on the command line will be filtered out.
    """
    present = []
    if (
        param.name
        and ctx.get_parameter_source(param.name) is not ParameterSource.DEFAULT
    ):
        present = [app.label for app in (ctx.params.get(param.name) or [])]
    ret = [
        CompletionItem(app.label)
        for app in apps.get_app_configs()
        if app.label.startswith(incomplete) and app.label not in present
    ]
    if not ret and incomplete:
        ret = [
            CompletionItem(app.name)
            for app in apps.get_app_configs()
            if app.name.startswith(incomplete)
            and app.name not in present
            and app.label not in present
        ]
    return ret


def complete_import_path(
    ctx: Context, param: Parameter, incomplete: str
) -> t.List[CompletionItem]:
    """
    A completer that completes a python dot import path string based on sys.path.

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :return: A list of available matching import paths
    """
    incomplete = incomplete.strip()
    completions = []
    packages = [pkg for pkg in incomplete.split(".") if pkg]
    pkg_complete = not incomplete or incomplete.endswith(".")
    module_import = ".".join(packages) if pkg_complete else ".".join(packages[:-1])
    module_path = Path(module_import.replace(".", "/"))
    search_paths = []
    for pth in sys.path:
        if (Path(pth) / module_path).exists():
            search_paths.append(str(Path(pth) / module_path))

    prefix = "" if pkg_complete else packages[-1]
    for module in pkgutil.iter_modules(path=search_paths):
        if module.name.startswith(prefix):
            completions.append(
                CompletionItem(
                    f'{module_import}{"." if module_import else ""}{module.name}',
                    type="dir",
                )
            )
    if len(completions) == 1 and not completions[0].value.endswith("."):
        return (
            complete_import_path(ctx, param, f"{completions[0].value}.") or completions
        )
    return completions


def complete_path(
    ctx: Context, param: Parameter, incomplete: str, dir_only: t.Optional[bool] = None
) -> t.List[CompletionItem]:
    """
    A completer that completes a path. Relative incomplete paths are interpreted relative to
    the current working directory.

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :param dir_only: Restrict completions to paths to directories only, otherwise complete
        directories or files.
    :return: A list of available matching directories
    """

    def exists(pth: Path) -> bool:
        if dir_only:
            return pth.is_dir()
        return pth.exists() or pth.is_symlink()

    completions = []
    incomplete_path = Path(incomplete)
    partial_dir = ""
    if not exists(incomplete_path) and not incomplete.endswith(os.sep):
        partial_dir = incomplete_path.name
        incomplete_path = incomplete_path.parent
    elif incomplete_path.is_file() and not dir_only:
        return [CompletionItem(incomplete, type="file")]
    if incomplete_path.is_dir():
        for child in os.listdir(incomplete_path):
            if not exists(incomplete_path / child):
                continue
            if child.startswith(partial_dir):
                to_complete = incomplete[0 : (-len(partial_dir) or None)]
                completions.append(
                    CompletionItem(
                        f"{to_complete}"
                        f"{'' if not to_complete or to_complete.endswith(os.sep) else os.sep}"
                        f"{child}",
                        type="dir" if (incomplete_path / child).is_dir() else "file",
                    )
                )
    if (
        len(completions) == 1
        and Path(completions[0].value).is_dir()
        and [
            child
            for child in os.listdir(completions[0].value)
            if exists(Path(completions[0].value) / child)
        ]
    ):
        # recurse because we can go futher
        return complete_path(ctx, param, completions[0].value, dir_only=dir_only)
    return completions


complete_directory = partial(complete_path, dir_only=True)
"""
A completer that completes a directory path (but not files). Relative incomplete paths
are interpreted relative to the current working directory.

:param ctx: The click context.
:param param: The click parameter.
:param incomplete: The incomplete string.
:return: A list of available matching directories
"""


def these_strings(
    strings: t.Union[t.Callable[[], Strings], Strings],
    allow_duplicates: bool = False,
):
    """
    Get a completer that provides completion logic that matches the allowed strings.

    :param strings: A sequence of allowed strings or a callable that generates a sequence of
        allowed strings.
    :param allow_duplicates: Whether or not to allow duplicate values. Defaults to False.
    :return: A completer function.
    """

    def complete(ctx: Context, param: Parameter, incomplete: str):
        present = []
        if (
            not allow_duplicates
            and param.name
            and ctx.get_parameter_source(param.name) is not ParameterSource.DEFAULT
        ):
            present = [value for value in (ctx.params.get(param.name) or [])]
        return [
            CompletionItem(item)
            for item in (strings() if callable(strings) else strings)
            if item.startswith(incomplete) and item not in present
        ]

    return complete


# use a function that returns a generator because we should not access settings on import
databases = partial(these_strings, lambda: settings.DATABASES.keys())
"""
A completer that completes Django database aliases configured in settings.DATABASES.

:param allow_duplicates: Whether or not to allow duplicate values. Defaults to False.
:return: A completer function.
"""

commands = partial(these_strings, lambda: get_commands().keys())
"""
A completer that completes management command names.

:param allow_duplicates: Whether or not to allow duplicate values. Defaults to False.
:return: A completer function.
"""


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
    :param allow_duplicates: If False (default) remove completions from previously provided
        values.
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
