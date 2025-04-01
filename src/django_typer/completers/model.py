import typing as t
from datetime import date, time, timedelta
from functools import partial

from click import Context, Parameter
from click.core import ParameterSource
from click.shell_completion import CompletionItem
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet


def int_ranges(incomplete: str, max_val: int) -> t.List[t.Tuple[int, int]]:
    lower = int(incomplete)
    neg = lower < 0
    lower = abs(lower)
    upper = abs(lower + 1)
    ranges = [(-upper, -lower)] if neg else [(lower, upper)]
    while (lower := lower * 10) <= max_val:
        upper *= 10
        ranges.append((-upper, -lower) if neg else (lower, upper))
    return ranges


def int_query(
    incomplete: str,
    lookup_field: str,
    queryset: QuerySet,
    **_,
) -> models.Q:
    """
    The default completion query builder for integer fields. This method will
    return a Q object that will match any value that starts with the incomplete
    string. For example, if the incomplete string is "1", the query will match
    1, 10-19, 100-199, 1000-1999, etc.

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :param queryset: The starting queryset to use to determine integer ranges.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid integer.
    :raises TypeError: If the incomplete string is not a valid integer.
    """
    qry = models.Q()
    neg = incomplete.startswith("-")
    for lower, upper in int_ranges(
        incomplete,
        queryset.aggregate(models.Max(lookup_field))[f"{lookup_field}__max"],
    ):
        qry |= models.Q(
            **{f"{lookup_field}__gt{'' if neg else 'e'}": lower}
        ) & models.Q(**{f"{lookup_field}__lt{'e' if neg else ''}": upper})
    return qry


def float_query(
    incomplete: str, lookup_field: str, queryset: QuerySet, **_
) -> models.Q:
    """
    The default completion query builder for float fields. This method will
    return a Q object that will match any value that starts with the incomplete
    string. For example, if the incomplete string is "1.1", the query will match
    1.1 <= float(incomplete) < 1.2

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :param queryset: The starting queryset to use to determine float ranges.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid float.
    :raises TypeError: If the incomplete string is not a valid float.
    """
    incomplete = incomplete.rstrip("0").rstrip(".")
    lower = float(incomplete)
    if "." in incomplete:
        upper = lower + float(
            f"0.{'0' * (len(incomplete) - incomplete.index('.') - 2)}1"
        )
    else:
        return int_query(
            incomplete=incomplete, lookup_field=lookup_field, queryset=queryset
        )
    return models.Q(**{f"{lookup_field}__gte": lower}) & models.Q(
        **{f"{lookup_field}__lt": upper}
    )


def text_query(
    incomplete: str, lookup_field: str, case_insensitive: bool = False, **_
) -> models.Q:
    """
    The default completion query builder for text-based fields. This method will
    return a Q object that will match any value that starts with the incomplete
    string. Case sensitivity is determined by the case_insensitive constructor
    parameter.

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :param case_insensitive: If the lookup should be case insensitive or not.
    :return: A Q object to use for filtering the queryset.
    """
    if case_insensitive:
        return models.Q(**{f"{lookup_field}__istartswith": incomplete})
    return models.Q(**{f"{lookup_field}__startswith": incomplete})


def uuid_query(incomplete: str, lookup_field: str, **_) -> t.Tuple[models.Q, int]:
    """
    The default completion query builder for UUID fields. This method will
    return a Q object that will match any value that starts with the incomplete
    string. The incomplete string will be stripped of all non-alphanumeric
    characters and padded with zeros to 32 characters. For example, if the
    incomplete string is "a", the query will match
    a0000000-0000-0000-0000-000000000000 to affffffff-ffff-ffff-ffff-ffffffffffff.

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :return: A 2-tuple where the first element is the Q object to use for filtering the
        queryset and the second is the integer offset into the incomplete string where
        the completion characters should be concatenated.
    :raises ValueError: If the incomplete string is too long or contains invalid
        UUID characters. Anything other than (0-9a-fA-F).
    """
    from uuid import UUID

    # the offset futzing is to allow users to ignore the - in the UUID
    # as a convenience of its implementation any non-alpha numeric character
    # will be ignored, and the completion suggestions and parsing will still work
    uuid = ""
    offset = 0
    for char in incomplete:
        if char.isalnum():
            uuid += char
        else:
            offset -= 1

    if len(incomplete) >= 9:
        offset += 1
    if len(incomplete) >= 14:
        offset += 1
    if len(incomplete) >= 19:
        offset += 1
    if len(incomplete) >= 24:
        offset += 1

    if len(uuid) > 32:
        raise ValueError(f"Too many UUID characters: {incomplete}")
    min_uuid = UUID(uuid + "0" * (32 - len(uuid)))
    max_uuid = UUID(uuid + "f" * (32 - len(uuid)))
    return (
        models.Q(**{f"{lookup_field}__gte": min_uuid})
        & models.Q(**{f"{lookup_field}__lte": max_uuid}),
        offset,
    )


def date_query(incomplete: str, lookup_field: str, **_) -> models.Q:
    """
    Default completion query builder for date fields. This method will return a Q
    object that will match any value that starts with the incomplete date string.
    All dates must be in ISO8601 format (YYYY-MM-DD).

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid partial date.
    :raises AssertionError: If the incomplete string is not a valid partial date.
    """
    lower_bound, upper_bound = get_date_bounds(incomplete)
    return models.Q(**{f"{lookup_field}__gte": lower_bound}) & models.Q(
        **{f"{lookup_field}__lte": upper_bound}
    )


def time_query(incomplete: str, lookup_field: str, **_) -> models.Q:
    """
    Default completion query builder for time fields. This method will return a Q
    object that will match any value that starts with the incomplete time string.
    All times must be in ISO 8601 format (HH:MM:SS.ssssss).

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid partial time.
    :raises AssertionError: If the incomplete string is not a valid partial time.
    """
    lower_bound, upper_bound = get_time_bounds(incomplete)
    return models.Q(**{f"{lookup_field}__gte": lower_bound}) & models.Q(
        **{f"{lookup_field}__lte": upper_bound}
    )


def datetime_query(incomplete: str, lookup_field: str, **_) -> models.Q:
    """
    Default completion query builder for datetime fields. This method will return a
    Q object that will match any value that starts with the incomplete datetime
    string. All dates must be in ISO8601 format (YYYY-MM-DDTHH:MM:SS.ssssss±HH:MM).

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid partial datetime.
    :raises AssertionError: If the incomplete string is not a valid partial
        datetime.
    """
    import re
    from datetime import datetime

    from django.utils.timezone import get_default_timezone, make_aware

    parts = incomplete.split("T")
    lower_bound, upper_bound = get_date_bounds(parts[0])

    def get_tz_part(dt_str: str) -> str:
        return dt_str[dt_str.rindex("+") if "+" in dt_str else dt_str.rindex("-") :]

    time_lower = datetime.min.time()
    time_upper = datetime.max.time()
    tz_part = ""
    if len(parts) > 1:
        time_parts = re.split(r"[+-]", parts[1])
        time_lower, time_upper = get_time_bounds(time_parts[0])
        # we punt on the timezones - if the user supplies a partial timezone
        # different than the default django timezone, its just too complicated to be
        # worth trying to complete, we ensure it aligns as a prefix to the
        # configured default timezone instead
        if len(time_parts) > 1 and parts[1]:
            tz_part = get_tz_part(parts[1])
    lower_bound = datetime.combine(lower_bound, time_lower)
    upper_bound = datetime.combine(upper_bound, time_upper)

    if settings.USE_TZ:
        lower_bound = make_aware(lower_bound, get_default_timezone())
        upper_bound = make_aware(upper_bound, get_default_timezone())
        db_tz_part = get_tz_part(lower_bound.isoformat())
        assert db_tz_part.startswith(tz_part)
    else:
        assert not tz_part
    return models.Q(**{f"{lookup_field}__gte": lower_bound}) & models.Q(
        **{f"{lookup_field}__lte": upper_bound}
    )


def duration_query(
    incomplete: str, lookup_field: str, queryset: QuerySet, **_
) -> models.Q:
    """
    Default completion query builder for duration fields. This method will return a
    Q object that will match any value that is greater than the incomplete duration
    string (or less if negative). Duration strings are formatted in a subset of the
    ISO8601 standard. Only day, hours, minutes and fractional seconds are supported.
    Year, week and month specifiers are not.

    **This query will utilize the database index if one exists.**

    :param incomplete: The incomplete string.
    :param lookup_field: The name of the model field to use for lookup.
    :param queryset: The queryset to use to determine integer ranges.
    :return: A Q object to use for filtering the queryset.
    :raises ValueError: If the incomplete string is not a valid partial duration.
    :raises AssertionError: If the incomplete string is not a valid partial
        duration.
    """
    from django_typer.utils import parse_iso_duration

    duration, ambiguity = parse_iso_duration(incomplete)
    if incomplete.endswith("S") or (duration.microseconds and not ambiguity):
        return models.Q(**{f"{lookup_field}": duration})
    neg = incomplete.startswith("-")

    qry = models.Q()
    horizon = None  # time horizon is exclusive!

    if ambiguity and "T" not in incomplete and "D" not in incomplete:
        # days is unbounded
        # if days == 5, we want to match 5-<6, 50-<60, 500-<600, etc
        max_val = (
            queryset.filter(qry).aggregate(models.Min(lookup_field))[
                f"{lookup_field}__min"
            ]
            if neg
            else queryset.filter(qry).aggregate(models.Max(lookup_field))[
                f"{lookup_field}__max"
            ]
        )
        for lower, upper in int_ranges(
            ambiguity,
            max_val.days,
        ):
            qry |= models.Q(
                **{f"{lookup_field}__gt{'' if neg else 'e'}": timedelta(days=lower)}
            ) & models.Q(
                **{f"{lookup_field}__lt{'e' if neg else ''}": timedelta(days=upper)}
            )
    elif duration.days or "D" in incomplete or "T" in incomplete:
        horizon = timedelta(days=1)

    if "T" in incomplete:
        hours, seconds = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        # if we are here, we may or may not have an ambiguous time component
        # or (exclusively) we may be missing time components
        if ambiguity is None:
            # handle no ambiguity first
            # there's no way to be here and have any ambiguity or non-ambiguous
            # microseconds ex: PT PT1. PT1M PT1H PT1H1M
            if incomplete.endswith("M"):
                horizon = timedelta(minutes=1)
            elif incomplete.endswith("H"):
                horizon = timedelta(hours=1)
            elif not incomplete.endswith("T"):
                horizon = timedelta(seconds=1)
        else:
            # we have a trailing ambiguity
            if "." in incomplete or seconds:
                # microsecond ambiguity
                # 5.000 -> the most this could be is 5.000999
                floor = int(f"{ambiguity:0<6}")
                duration = timedelta(
                    days=abs(duration.days),
                    seconds=abs(duration.seconds),
                    microseconds=floor,
                )
                duration = -duration if neg else duration
                horizon = timedelta(
                    microseconds=int(ambiguity + "9" * (6 - len(ambiguity))) + 1 - floor
                )
            else:
                # ambiguity is at least a seconds ambiguity
                int_amb = int(ambiguity)
                compound_horizon: t.List[
                    t.Tuple[int, int]
                ] = []  # seconds horizons small -> large
                compound_horizon.append(
                    (
                        int_amb,
                        int_amb + 1,
                    )
                )
                compound_horizon.append(
                    (int(f"{ambiguity}0"), min(int(f"{ambiguity}9") + 1, 60))
                )
                if "M" not in incomplete:
                    # ambiguity is minutes or seconds
                    compound_horizon.append(
                        (
                            int_amb * 60,
                            int_amb * 60 + 60,
                        )
                    )
                    if len(ambiguity) == 1:
                        compound_horizon.append(
                            (
                                int(f"{ambiguity}0") * 60,
                                min(int(f"{ambiguity}9") + 1, 60) * 60,
                            )
                        )
                if "H" not in incomplete:
                    # ambiguity is hours or minutes or seconds
                    # bug here T1 could be T1H or T10H-T19H
                    compound_horizon.append(
                        (
                            int_amb * 3600,
                            int_amb * 3600 + 3600,
                        )
                    )
                    if len(ambiguity) == 1:
                        compound_horizon.append(
                            (
                                int(f"{ambiguity}0") * 3600,
                                min(int(f"{ambiguity}9") + 1, 24) * 3600,
                            )
                        )
                c_qry = models.Q()
                for lower, upper in compound_horizon:
                    lwr, upr = (
                        (
                            duration - timedelta(seconds=upper),
                            duration - timedelta(seconds=lower),
                        )
                        if neg
                        else (
                            duration + timedelta(seconds=lower),
                            duration + timedelta(seconds=upper),
                        )
                    )
                    h_qry = models.Q(
                        **{f"{lookup_field}__gt{'' if neg else 'e'}": lwr}
                    ) & models.Q(**{f"{lookup_field}__lt{'e' if neg else ''}": upr})
                    c_qry |= h_qry
                qry &= c_qry

    inclusive = "" if incomplete.endswith("T") and duration.days else "e"
    qry &= (
        models.Q(**{f"{lookup_field}__lt{inclusive}": duration})
        if neg
        else models.Q(**{f"{lookup_field}__gt{inclusive}": duration})
    )

    if horizon:
        qry &= (
            models.Q(**{f"{lookup_field}__gt": duration - horizon})
            if neg
            else models.Q(**{f"{lookup_field}__lt": duration + horizon})
        )
    return qry


def get_date_bounds(incomplete: str) -> t.Tuple[date, date]:
    """
    Turn an incomplete YYYY-MM-DD date string into upper and lower bound date
    objects.

    :param incomplete: The incomplete time string.
    :return: A 2-tuple of (lower, upper) date object boundaries.
    """
    import calendar

    parts = incomplete.split("-")
    year_low = max(int(parts[0] + "0" * (4 - len(parts[0]))), 1)
    year_high = int(parts[0] + "9" * (4 - len(parts[0])))
    month_high = 12
    month_low = 1
    day_low = 1
    day_high = None
    if len(parts) > 1:
        assert len(parts[0]) > 3, "Year must be 4 digits"
        month_high = min(int(parts[1] + "9" * (2 - len(parts[1]))), 12)
        month_low = max(int(parts[1] + "0" * (2 - len(parts[1]))), 1)
        if len(parts) > 2:
            assert len(parts[1]) > 1, "Month must be 2 digits"
            day_low = max(int(parts[2] + "0" * (2 - len(parts[2]))), 1)
            day_high = min(
                int(parts[2] + "9" * (2 - len(parts[2]))),
                calendar.monthrange(year_high, month_high)[1],
            )
    lower_bound = date(year=year_low, month=month_low, day=day_low)
    upper_bound = date(
        year=year_high,
        month=month_high,
        day=day_high or calendar.monthrange(year_high, month_high)[1],
    )
    return lower_bound, upper_bound


def get_time_bounds(incomplete: str) -> t.Tuple[time, time]:
    """
    Turn an incomplete HH::MM::SS.ssssss time string into upper and lower bound time
    objects.

    :param incomplete: The incomplete time string.
    :return: A 2-tuple of (lower, upper) time object boundaries.
    """
    time_parts = incomplete.split(":")
    if time_parts and time_parts[0]:
        hours_low = int(time_parts[0] + "0" * (2 - len(time_parts[0])))
        hours_high = min(int(time_parts[0] + "9" * (2 - len(time_parts[0]))), 23)
        minutes_low = 0
        minutes_high = 59
        seconds_low = 0
        seconds_high = 59
        microseconds_low = 0
        microseconds_high = 999999
        if len(time_parts) > 1:
            assert len(time_parts[0]) > 1  # Hours must be 2 digits
            minutes_low = int(time_parts[1] + "0" * (2 - len(time_parts[1])))
            minutes_high = min(int(time_parts[1] + "9" * (2 - len(time_parts[1]))), 59)
            if len(time_parts) > 2:
                seconds_parts = time_parts[2].split(".")
                int_seconds = seconds_parts[0]
                assert len(time_parts[1]) > 1  # Minutes must be 2 digits
                seconds_low = int(int_seconds + "0" * (2 - len(int_seconds)))
                seconds_high = min(int(int_seconds + "9" * (2 - len(int_seconds))), 59)
                if len(seconds_parts) > 1:
                    microseconds = seconds_parts[1]
                    microseconds_low = int(microseconds + "0" * (6 - len(microseconds)))
                    microseconds_high = int(
                        microseconds + "9" * (6 - len(microseconds))
                    )
        return time(
            hour=hours_low,
            minute=minutes_low,
            second=seconds_low,
            microsecond=microseconds_low,
        ), time(
            hour=hours_high,
            minute=minutes_high,
            second=seconds_high,
            microsecond=microseconds_high,
        )
    return time.min, time.max


class ModelObjectCompleter:
    """
    A completer for generic Django model objects. This completer will work
    for most Django core model field types where completion makes sense.

    This completer currently supports the following field types and their subclasses:

        - :class:`~django.db.models.IntegerField`
            - :class:`~django.db.models.AutoField`
            - :class:`~django.db.models.BigAutoField`
            - :class:`~django.db.models.BigIntegerField`
            - :class:`~django.db.models.SmallIntegerField`
            - :class:`~django.db.models.PositiveIntegerField`
            - :class:`~django.db.models.PositiveSmallIntegerField`
            - :class:`~django.db.models.SmallAutoField`
        - :class:`~django.db.models.CharField`
            - :class:`~django.db.models.SlugField`
            - :class:`~django.db.models.URLField`
            - :class:`~django.db.models.EmailField`
        - :class:`~django.db.models.FileField`
            - :class:`~django.db.models.ImageField`
        - :class:`~django.db.models.FilePathField`
        - :class:`~django.db.models.TextField`
        - :class:`~django.db.models.DateField` **(Must use ISO 8601: YYYY-MM-DD)**
        - :class:`~django.db.models.TimeField` **(Must use ISO 8601: HH:MM:SS.ssssss)**
        - :class:`~django.db.models.DateTimeField` **(Must use ISO 8601: YYYY-MM-DDTHH:MM:SS.ssssss±HH:MM)**
        - :class:`~django.db.models.DurationField` **(Must use ISO 8601: YYYY-MM-DDTHH:MM:SS.ssssss±HH:MM)**
        - :class:`~django.db.models.UUIDField`
        - :class:`~django.db.models.FloatField`
        - :class:`~django.db.models.DecimalField`
        - :class:`~django.db.models.GenericIPAddressField`

    .. note::

        The queries used by this completer will make use of column indexes. Completions
        should be fast even for large data.

    The completer query logic is pluggable, but the defaults cover most use cases. The
    limit field is important. It defaults to 50 meaning if more than 50 potential
    completions are found only the first 50 will be returned and there will be no
    indication to the user that there are more. This is to prevent the shell from
    becoming unresponsive when offering completion for large tables.

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

        See also :func:`~django_typer.utils.model_parser_completer` for a convenience
        function that returns a configured parser and completer for a model object
        and helps reduce boilerplate.

    :param model_or_qry: The Django model class or a queryset to filter against.
    :param lookup_field: The name of the model field to use for lookup.
    :param help_field: The name of the model field to use for help text or None if
        no help text should be provided.
    :param query: A callable that accepts any named arguments and returns a Q object.
        It will be passed:

        - **incomplete** the incomplete string
        - **lookup_field** the name of the model field to use for lookup
        - **queryset** the base queryset to use for completions
        - **context** the click context
        - **parameter** the click parameter
        - **completer** an instance of this ModelObjectCompleter class

        It is not required to use those arguments, but they are available.

        It must return a Q object to use for filtering the queryset. The default query
        will use the relevant query builder depending on the lookup field class.

        ..note::

            The query builder function may also return a second integer offset value.
            This value will be used to adjust the index into the completion strings when
            we concatenate the incomplete string with the lookup field value - see UUID
            which has to allow for - to be missing
    :param limit: The maximum number of completion items to return. If None, all
        matching items will be returned. When offering completion for large tables
        you'll want to set this to a reasonable limit. Default: 50
    :param case_insensitive: Whether or not to perform case insensitive matching when
        completing text-based fields. Defaults to False.
    :param distinct: Whether or not to filter out duplicate values. Defaults to True.
        This is not the same as calling distinct() on the queryset - which will happen
        regardless - but rather whether or not to filter out values that are already
        given for the parameter on the command line.
    :param order_by: The order_by parameter to prioritize completions in. By default
        the default queryset ordering will be used for the model.
    :param use_choices: Whether or not to use the field choices for completion. If True,
        matches to choice values coerced to strings will be returned. If False, the
        field's default query builder will be used instead.
    """

    QueryBuilder = t.Callable[
        ["ModelObjectCompleter", Context, Parameter, str], models.Q
    ]

    model_cls: t.Type[models.Model]
    queryset: QuerySet
    lookup_field: str
    help_field: t.Optional[str] = None
    query: t.Callable[..., t.Union[models.Q, t.Tuple[models.Q, int]]]
    limit: t.Optional[int] = 50
    case_insensitive: bool = False
    distinct: bool = True
    order_by: t.List[str] = []
    use_choices: bool = True

    _field: models.Field

    @staticmethod
    def to_str(obj: t.Any) -> str:
        """
        Convert the given object into a string suitable for use in completions.
        """
        from datetime import datetime

        from django.utils.timezone import get_default_timezone

        if isinstance(obj, datetime):
            if settings.USE_TZ and get_default_timezone():
                obj = obj.astimezone(get_default_timezone())
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            from django_typer.utils import duration_iso_string

            return duration_iso_string(obj)
        return str(obj)

    def __init__(
        self,
        model_or_qry: t.Union[t.Type[models.Model], QuerySet],
        lookup_field: t.Optional[str] = None,
        help_field: t.Optional[str] = help_field,
        query: t.Optional[QueryBuilder] = None,
        limit: t.Optional[int] = limit,
        case_insensitive: bool = case_insensitive,
        distinct: bool = distinct,
        order_by: t.Optional[t.Union[str, t.Sequence[str]]] = order_by,
        use_choices: bool = use_choices,
    ):
        import inspect

        if inspect.isclass(model_or_qry) and issubclass(model_or_qry, models.Model):
            self.model_cls = model_or_qry
            self.queryset = model_or_qry.objects.all()
        elif isinstance(model_or_qry, QuerySet):
            self.model_cls = model_or_qry.model
            self.queryset = model_or_qry
        else:
            raise ValueError(
                "ModelObjectCompleter requires a Django model class or queryset."
            )
        self.lookup_field = str(
            lookup_field or getattr(self.model_cls._meta.pk, "name", "id")
        )
        self.help_field = help_field
        self.limit = limit
        self.case_insensitive = case_insensitive
        self.distinct = distinct
        if order_by:
            self.order_by = [order_by] if isinstance(order_by, str) else list(order_by)
        self.use_choices = use_choices

        self._field = self.model_cls._meta.get_field(self.lookup_field)
        if query:
            self.query = query
        else:
            if isinstance(self._field, models.IntegerField):
                self.query = int_query
            elif isinstance(
                self._field,
                (
                    models.CharField,
                    models.TextField,
                    models.GenericIPAddressField,
                    models.FileField,
                    models.FilePathField,
                ),
            ):
                self.query = partial(
                    text_query,
                    case_insensitive=self.case_insensitive,
                )
            elif isinstance(self._field, models.UUIDField):
                self.query = uuid_query
            elif isinstance(self._field, (models.FloatField, models.DecimalField)):
                self.query = float_query
            elif isinstance(self._field, models.DateTimeField):
                self.query = datetime_query
            elif isinstance(self._field, models.DateField):
                self.query = date_query
            elif isinstance(self._field, models.TimeField):
                self.query = time_query
            elif isinstance(self._field, models.DurationField):
                self.query = duration_query
            else:
                raise ValueError(
                    f"Unsupported lookup field class: {self._field.__class__.__name__}"
                )

    def __call__(
        self, context: Context, parameter: Parameter, incomplete: str
    ) -> t.List[CompletionItem]:
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

        completion_qry = models.Q(**{self.lookup_field + "__isnull": False})

        offset = 0
        if incomplete:
            try:
                result = self.query(
                    incomplete=incomplete,
                    lookup_field=self.lookup_field,
                    queryset=self.queryset,
                    context=context,
                    parameter=parameter,
                    completer=self,
                )
                if isinstance(result, tuple):
                    completion_qry &= result[0]
                    offset = result[1] if len(result) > 1 else 0
                else:
                    completion_qry &= result
            except (ValueError, TypeError, AssertionError):
                return []

        columns = [self.lookup_field]
        if self.help_field:
            columns.append(self.help_field)

        excluded: t.List[models.Model] = []
        if (
            self.distinct
            and parameter.name
            and context.get_parameter_source(parameter.name)
            is not ParameterSource.DEFAULT
        ):
            excluded = context.params.get(parameter.name, []) or []

        qryset = self.queryset.filter(completion_qry).exclude(
            pk__in=[ex.pk for ex in excluded]
        )
        if self.order_by:
            qryset = qryset.order_by(*self.order_by)

        completions = []
        for values in qryset.distinct().values_list(*columns)[0 : self.limit]:
            str_value = self.to_str(values[0])
            if str_value:
                completions.append(
                    CompletionItem(
                        # use the incomplete string prefix incase this was a case
                        # insensitive match
                        value=incomplete + str_value[len(incomplete) + offset :],
                        help=values[1] if len(values) > 1 else None,
                    )
                )
        return completions
