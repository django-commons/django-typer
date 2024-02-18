"""
A collection of completer classes that can be used to quickly add shell completion
for various kinds of django objects.

# TODO: - add default query builders for these field types:
    GenericIPAddressField,
    TimeField,
    DateField,
    DateTimeField,
    DurationField,
    FilePathField,
    FileField
"""

import typing as t
from types import MethodType

from click import Context, Parameter
from click.shell_completion import CompletionItem
from django.apps import apps
from django.db.models import (
    CharField,
    DecimalField,
    FloatField,
    IntegerField,
    Max,
    Model,
    Q,
    TextField,
    UUIDField,
)


class ModelObjectCompleter:
    """
    A completer for generic Django model objects. This completer will work
    for any Django core model field where completion makes sense. For example,
    it will work for IntegerField, CharField, TextField, and UUIDField, but
    not for ForeignKey, ManyToManyField or BinaryField.

    The completer query logic is pluggable, but the defaults cover most use cases.

    :param model_cls: The Django model class to query.
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
    lookup_field: str
    help_field: t.Optional[str] = None
    query: MethodType
    limit: t.Optional[int] = 50
    case_insensitive: bool = False
    distinct: bool = True

    def default_query(
        self, context: Context, parameter: Parameter, incomplete: str
    ) -> Q:
        """
        The default completion query builder. This method will route to the
        appropriate query method based on the lookup field class.

        :param context: The click context.
        :param parameter: The click parameter.
        :param incomplete: The incomplete string.
        :return: A Q object to use for filtering the queryset.
        :raises ValueError: If the lookup field class is not supported or there
            is a problem using the incomplete string as a lookup given the field
            class.
        :raises TypeError: If there is a problem using the incomplete string as a
            lookup given the field class.
        """
        field = self.model_cls._meta.get_field(  # pylint: disable=protected-access
            self.lookup_field
        )
        if issubclass(field.__class__, IntegerField):
            return self.int_query(context, parameter, incomplete)
        if issubclass(field.__class__, (CharField, TextField)):
            return self.text_query(context, parameter, incomplete)
        if issubclass(field.__class__, UUIDField):
            return self.uuid_query(context, parameter, incomplete)
        if issubclass(field.__class__, (FloatField, DecimalField)):
            return self.float_query(context, parameter, incomplete)
        raise ValueError(f"Unsupported lookup field class: {field.__class__.__name__}")

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
        max_val = self.model_cls.objects.aggregate(Max(self.lookup_field))["id__max"]
        qry = Q(**{f"{self.lookup_field}": lower})
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
        if "." not in incomplete:
            return self.int_query(context, parameter, incomplete)
        incomplete = incomplete.rstrip("0")
        lower = float(incomplete)
        upper = lower + float(f'0.{"0"*(len(incomplete)-incomplete.index(".")-2)}1')
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
        uuid = ""
        for char in incomplete:
            if char.isalnum():
                uuid += char
        if len(uuid) > 32:
            raise ValueError(f"Too many UUID characters: {incomplete}")
        min_uuid = uuid + "0" * (32 - len(uuid))
        max_uuid = uuid + "f" * (32 - len(uuid))
        return Q(**{f"{self.lookup_field}__gte": min_uuid}) & Q(
            **{f"{self.lookup_field}__lte": max_uuid}
        )

    def __init__(
        self,
        model_cls: t.Type[Model],
        lookup_field: t.Optional[str] = None,
        help_field: t.Optional[str] = help_field,
        query: QueryBuilder = default_query,
        limit: t.Optional[int] = limit,
        case_insensitive: bool = case_insensitive,
        distinct: bool = distinct,
    ):
        self.model_cls = model_cls
        self.lookup_field = lookup_field or model_cls._meta.pk.name
        self.help_field = help_field
        self.query = MethodType(query, self)
        self.limit = limit
        self.case_insensitive = case_insensitive
        self.distinct = distinct

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
        if self.distinct and parameter.name:
            excluded = context.params.get(parameter.name, []) or []

        return [
            CompletionItem(
                # use the incomplete string prefix incase this was a case insensitive match
                value=incomplete
                + str(getattr(obj, self.lookup_field))[len(incomplete) :],
                help=getattr(obj, self.help_field, None) if self.help_field else "",
            )
            for obj in self.model_cls.objects.filter(completion_qry).distinct()[
                0 : self.limit
            ]
            if str(getattr(obj, self.lookup_field)) and obj not in excluded
        ]


def complete_app_label(ctx: Context, param: Parameter, incomplete: str):
    """
    A case-insensitive completer for Django app labels or names. The completer
    prefers labels but names will also work.

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :return: A list of matching app labels or names. Labels already present for the
        parameter on the command line will be filtered out.
    """
    present = [app.label for app in (ctx.params.get(param.name or "") or [])]
    ret = [
        app.label
        for app in apps.get_app_configs()
        if app.label.startswith(incomplete) and app.label not in present
    ]
    if not ret and incomplete:
        ret = [
            app.name
            for app in apps.get_app_configs()
            if app.name.startswith(incomplete)
            and app.name not in present
            and app.label not in present
        ]
    return ret
