"""
Typer_ supports custom parsers for options and arguments. If you would
like to type a parameter with a type that isn't supported by Typer_ you can
`implement your own parser <https://typer.tiangolo.com/tutorial/parameter-types/custom-types>`_
, or `ParamType <https://click.palletsprojects.com/en/8.1.x/api/#click.ParamType>`_
in click_ parlance.

This module contains a collection of parsers that turn strings into useful
Django types. Pass these parsers to the `parser` argument of typer.Option and
typer.Argument. Parsers are provided for:

- **Model Objects**: Turn a string into a model object instance using :class:`ModelObjectParser`.
- **App Labels**: Turn a string into an AppConfig instance using :func:`parse_app_label`.


.. warning::

    If you implement a custom parser, please take care to ensure that it:
        - Handles the case where the value is already the expected type.
        - Returns None if the value is None (already implemented if subclassing ParamType).
        - Raises a CommandError if the value is invalid.
        - Handles the case where the param and context are None.
"""

import typing as t
from uuid import UUID

from click import Context, Parameter, ParamType
from django.apps import AppConfig, apps
from django.core.management import CommandError
from django.db.models import Field, ForeignObjectRel, Model, UUIDField
from django.utils.translation import gettext as _

from django_typer.completers import ModelObjectCompleter


class ModelObjectParser(ParamType):
    """
    A parser that will turn strings into model object instances based on the
    configured lookup field and model class.

    .. code-block:: python

        from django_typer.parsers import ModelObjectParser

        class Command(TyperCommand):
            def handle(
                self,
                django_apps: Annotated[
                    t.List[MyModel],
                    typer.Argument(
                        parser=ModelObjectParser(MyModel, lookup_field="name"),
                        help=_("One or more application labels."),
                    ),
                ],
            ):

    .. note::

        Typer_ does not respect the shell_complete functions on ParamTypes passed as
        parsers. To add shell_completion see :class:`~django_typer.completers.ModelObjectCompleter`
        or the :func:`~django_typer.model_parser_completer` convenience
        function.

    :param model_cls: The model class to use for lookup.
    :param lookup_field: The field to use for lookup. Defaults to 'pk'.
    :param on_error: A callable that will be called if the lookup fails.
        The callable should accept three arguments: the model class, the
        value that failed to lookup, and the exception that was raised.
        If not provided, a CommandError will be raised.
    """

    error_handler = t.Callable[[t.Type[Model], str, Exception], None]

    model_cls: t.Type[Model]
    lookup_field: str
    case_insensitive: bool = False
    on_error: t.Optional[error_handler] = None

    _lookup: str = ""
    _field: Field
    _completer: ModelObjectCompleter

    __name__: str = "MODEL"  # typer internals expect this

    def __init__(
        self,
        model_cls: t.Type[Model],
        lookup_field: t.Optional[str] = None,
        case_insensitive: bool = case_insensitive,
        on_error: t.Optional[error_handler] = on_error,
    ):
        from django.contrib.contenttypes.fields import GenericForeignKey

        self.model_cls = model_cls
        self.lookup_field = str(
            lookup_field or getattr(self.model_cls._meta.pk, "name", "id")
        )
        self.on_error = on_error
        self.case_insensitive = case_insensitive
        field = self.model_cls._meta.get_field(self.lookup_field)
        assert not isinstance(field, (ForeignObjectRel, GenericForeignKey)), _(
            "{cls} is not a supported lookup field."
        ).format(cls=self._field.__class__.__name__)
        self._field = field
        if self.case_insensitive and "iexact" in self._field.get_lookups():
            self._lookup = "__iexact"
        self.__name__ = (
            str(self.model_cls._meta.verbose_name)
            if self.model_cls._meta.verbose_name
            else self.model_cls.__name__
        )

    def convert(
        self, value: t.Any, param: t.Optional[Parameter], ctx: t.Optional[Context]
    ):
        """
        Invoke the parsing action on the given string. If the value is
        already a model instance of the expected type the value will
        be returned. Otherwise the value will be treated as a value to query
        against the lookup_field. If no model object is found the error
        handler is invoked if one was provided.

        :param value: The value to parse.
        :param param: The parameter that the value is associated with.
        :param ctx: The context of the command.
        :raises CommandError: If the lookup fails and no error handler is
            provided.
        """
        try:
            if isinstance(value, self.model_cls):
                return value
            if isinstance(self._field, UUIDField):
                uuid = ""
                for char in value:
                    if char.isalnum():
                        uuid += char
                value = UUID(uuid)
            return self.model_cls.objects.get(
                **{f"{self.lookup_field}{self._lookup}": value}
            )
        except (self.model_cls.DoesNotExist, ValueError) as err:
            if self.on_error:
                return self.on_error(self.model_cls, str(value), err)
            raise CommandError(
                _('{model} "{value}" does not exist!').format(
                    model=self.model_cls.__name__, value=value
                )
            ) from err


def parse_app_label(label: t.Union[str, AppConfig]):
    """
    A parser for app labels. If the label is already an AppConfig instance,
    the instance is returned. The label will be tried first, if that fails
    the label will be treated as the app name.

    .. code-block:: python

        import typing as t
        import typer
        from django_typer import TyperCommand
        from django_typer.parsers import parse_app_label

        class Command(TyperCommand):

            def handle(
                self,
                django_apps: t.Annotated[
                    t.List[AppConfig],
                    typer.Argument(
                        parser=parse_app_label,
                        help=_("One or more application labels.")
                    )
                ]
            ):
                ...

    :param label: The label to map to an AppConfig instance.
    :raises CommandError: If no matching app can be found.
    """
    if isinstance(label, AppConfig):
        return label
    try:
        return apps.get_app_config(label)
    except LookupError as err:
        for cfg in apps.get_app_configs():
            if cfg.name == label:
                return cfg

        raise CommandError(
            _("{label} does not match any installed app label.").format(label=label)
        ) from err


parse_app_label.__name__ = "APP_LABEL"
