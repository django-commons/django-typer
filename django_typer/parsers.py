"""
A collection of parsers that turn strings into useful Django types.
Pass these parsers to the `parser` argument of typer.Option and
typer.Argument.
"""

import typing as t
from uuid import UUID

from django.apps import AppConfig, apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError
from django.db.models import Field, Model, UUIDField
from django.utils.translation import gettext as _


class ModelObjectParser:
    """
    A parser that will turn strings into model object instances based on the
    configured lookup field and model class.

    :param model_cls: The model class to use for lookup.
    :param lookup_field: The field to use for lookup. Defaults to 'pk'.
    :param on_error: A callable that will be called if the lookup fails.
        The callable should accept three arguments: the model class, the
        value that failed to lookup, and the exception that was raised.
        If not provided, a CommandError will be raised.
    """

    error_handler = t.Callable[[t.Type[Model], str, ObjectDoesNotExist], None]

    model_cls: t.Type[Model]
    lookup_field: str
    case_insensitive: bool = False
    on_error: t.Optional[error_handler] = None

    _lookup = ""
    _field: Field

    __name__ = "ModelObjectParser"  # typer internals expect this

    def __init__(
        self,
        model_cls: t.Type[Model],
        lookup_field: t.Optional[str] = None,
        case_insensitive: bool = case_insensitive,
        on_error: t.Optional[error_handler] = on_error,
    ):
        self.model_cls = model_cls
        self.lookup_field = lookup_field or model_cls._meta.pk.name
        self.on_error = on_error
        self.case_insensitive = case_insensitive
        self._field = self.model_cls._meta.get_field(self.lookup_field)
        if self.case_insensitive and "iexact" in self._field.get_lookups():
            self._lookup = "__iexact"

    def __call__(self, value: t.Union[str, Model]) -> Model:
        """
        Invoke the parsing action on the given string. If the value is
        already a model instance of the expected type the value will
        be returned. Otherwise the value will be treated as a value to query
        against the lookup_field. If no model object is found the error
        handler is invoked if one was provided.

        :param value: The value to parse.
        :raises CommandError: If the lookup fails and no error handler is
            provided.
        """
        try:
            if isinstance(value, self.model_cls):  # pragma: no cover
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
                return self.on_error(self.model_cls, value, err)
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

    :param label: The label to map to an AppConfig instance.
    :raises CommandError: If no matching app can be found.
    """
    if isinstance(label, AppConfig):  # pragma: no cover
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
