import typing as t
from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from click import Context, Parameter, ParamType
from django.core.management import CommandError
from django.db import models

from django_typer.completers.model import ModelObjectCompleter


class ReturnType(Enum):
    MODEL_INSTANCE = 0
    """Return the model instance with the matching field value."""

    FIELD_VALUE = 1
    """Return the value of the field that was matched."""

    QUERY_SET = 2
    """Return a queryset of model instances that match the field value."""


class ModelObjectParser(ParamType):
    """
    A parser that will turn strings into model object instances based on the
    configured lookup field and model class.

    .. code-block:: python

        from django_typer.parsers.model import ModelObjectParser

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
        parsers. To add shell_completion see
        :class:`~django_typer.completers.ModelObjectCompleter` or the
        :func:`~django_typer.utils.model_parser_completer` convenience function.

    :param model_cls: The model class to use for lookup.
    :param lookup_field: The field to use for lookup. Defaults to 'pk'.
    :param on_error: A callable that will be called if the lookup fails.
        The callable should accept three arguments: the model class, the
        value that failed to lookup, and the exception that was raised.
        If not provided, a CommandError will be raised.
    :param return_type: The model object parser can return types other than the model
        instance (default) - use the ReturnType enumeration to return other types
        from the parser including QuerySets or the primitive values of the model fields.
    """

    error_handler = t.Callable[[t.Type[models.Model], str, Exception], None]

    model_cls: t.Type[models.Model]
    lookup_field: str
    case_insensitive: bool = False
    on_error: t.Optional[error_handler] = None
    return_type: ReturnType = ReturnType.MODEL_INSTANCE

    _lookup: str = ""
    _field: models.Field
    _completer: ModelObjectCompleter

    __name__: str = "MODEL"  # typer internals expect this

    def _get_metavar(self) -> str:
        if isinstance(self._field, models.IntegerField):
            return "INT"
        elif isinstance(self._field, models.EmailField):
            return "EMAIL"
        elif isinstance(self._field, models.URLField):
            return "URL"
        elif isinstance(self._field, models.GenericIPAddressField):
            return "[IPv4|IPv6]"
        elif isinstance(self._field, models.UUIDField):
            return "UUID"
        elif isinstance(self._field, (models.FloatField, models.DecimalField)):
            return "FLOAT"
        elif isinstance(self._field, (models.FileField, models.FilePathField)):
            return "PATH"
        elif isinstance(self._field, models.DateTimeField):
            return "ISO 8601"
        elif isinstance(self._field, models.DateField):
            return "YYYY-MM-DD"
        elif isinstance(self._field, models.TimeField):
            return "HH:MM:SS.sss"
        elif isinstance(self._field, models.DurationField):
            return "ISO 8601"
        return "TXT"

    def __init__(
        self,
        model_cls: t.Type[models.Model],
        lookup_field: t.Optional[str] = None,
        case_insensitive: bool = case_insensitive,
        on_error: t.Optional[error_handler] = on_error,
        return_type: ReturnType = return_type,
    ):
        from django.contrib.contenttypes.fields import GenericForeignKey

        self.model_cls = model_cls
        self.lookup_field = str(
            lookup_field or getattr(self.model_cls._meta.pk, "name", "id")
        )
        self.on_error = on_error
        self.return_type = return_type
        self.case_insensitive = case_insensitive
        field = self.model_cls._meta.get_field(self.lookup_field)
        assert not isinstance(field, (models.ForeignObjectRel, GenericForeignKey)), (
            "{cls} is not a supported lookup field."
        ).format(cls=self._field.__class__.__name__)
        self._field = field
        if self.case_insensitive and "iexact" in self._field.get_lookups():
            self._lookup = "__iexact"
        self.__name__ = self._get_metavar()

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
        original = value
        try:
            if not isinstance(value, str):
                return value
            elif isinstance(self._field, models.UUIDField):
                uuid = ""
                for char in value:
                    if char.isalnum():
                        uuid += char
                value = UUID(uuid)
            elif isinstance(self._field, models.DateTimeField):
                value = datetime.fromisoformat(value)
            elif isinstance(self._field, models.DateField):
                value = date.fromisoformat(value)
            elif isinstance(self._field, models.TimeField):
                value = time.fromisoformat(value)
            elif isinstance(self._field, models.DurationField):
                from django_typer.utils import parse_iso_duration

                parsed, ambiguous = parse_iso_duration(value)
                if ambiguous:
                    raise ValueError(f"Invalid duration: {value}")
                value = parsed
            if self.return_type is ReturnType.QUERY_SET:
                return self.model_cls.objects.filter(
                    **{f"{self.lookup_field}{self._lookup}": value}
                )
            elif self.return_type is ReturnType.FIELD_VALUE:
                return value
            return self.model_cls.objects.get(
                **{f"{self.lookup_field}{self._lookup}": value}
            )
        except ValueError as err:
            if self.on_error:
                return self.on_error(self.model_cls, original, err)
            raise CommandError(
                f"{original} is not a valid {self._field.__class__.__name__}"
            ) from err
        except self.model_cls.DoesNotExist as err:
            if self.on_error:
                return self.on_error(self.model_cls, original, err)
            raise CommandError(
                f"{self.model_cls.__name__}.{self.lookup_field}='{original}' does not "
                "exist!"
            ) from err
