r"""
::

      ___ _                           _____                       
     /   (_) __ _ _ __   __ _  ___   /__   \_   _ _ __   ___ _ __ 
    / /\ / |/ _` | '_ \ / _` |/ _ \    / /\/ | | | '_ \ / _ \ '__|
   / /_//| | (_| | | | | (_| | (_) |  / /  | |_| | |_) |  __/ |   
  /___,'_/ |\__,_|_| |_|\__, |\___/   \/    \__, | .__/ \___|_|   
       |__/             |___/               |___/|_|              


django-typer_ provides an extension class, :class:`~django_typer.TyperCommand`, to the 
BaseCommand_ class that melds the Typer_/click_ infrastructure with
the Django_ infrastructure. The result is all the ease of specifying commands, groups
and options and arguments using Typer_ and click_ in a way that feels like and is
interface compatible with Django_'s BaseCommand_ This should enable a smooth transition
for existing Django_ commands and an intuitive feel for implementing new commands.

django-typer_ also supports shell completion for bash_, zsh_, fish_ and powershell_ and
extends that support to native Django_ management commands as well.


The goal of django-typer_ is to provide full Typer_ style functionality while maintaining
compatibility with the Django management command system. This means that the BaseCommand_
interface is preserved and the Typer_ interface is added on top of it. This means that
this code base is more robust to changes in the Django management command system - because
most of the base class functionality is preserved but many Typer_ and click_ internals are
used directly to achieve this. We rely on robust CI to catch breaking changes upstream.
"""

# During development of django-typer_ I've wrestled with a number of encumbrances in the
# aging django management command design. I detail them here mostly to keep track of them
# for possible future refactors of core Django.

# 1) BaseCommand::execute() prints results to stdout without attempting to convert them
# to strings. This means you've gotta do weird stuff to get a return object out of
# call_command()

# 2) call_command() converts arguments to strings. There is no official way to pass
# previously parsed arguments through call_command(). This makes it a bit awkward to
# use management commands as callable functions in django code which you should be able
# to easily do. django-typer allows you to invoke the command and group functions
# directly so you can work around this, but it would be nice if call_command() supported
# a general interface that all command libraries could easily implement to.

# 3) terminal autocompletion is not pluggable. As of this writing (Django<=5)
# autocomplete is implemented for bash only and has no mechanism for passing the buck
# down to command implementations. The result of this in django-typer is that we wrap
# django's autocomplete and pass the buck to it instead of the other way around. This is
# fine but it will be awkward if two django command line apps with their own autocomplete
# infrastructure are used together. Django should be the central coordinating point for
# this. This is the reason for the pluggable --fallback awkwardness in shellcompletion.

# 4) Too much of the BaseCommand implementation is built assuming argparse. A more
# generalized abstraction of this interface is in order. Right now BaseCommand is doing
# double duty both as a base class and a protocol.

# 5) There is an awkwardness to how parse_args flattens all the arguments and options
# into a single dictionary. This means that when mapping a library like Typer onto the
# BaseCommand interface you cannot allow arguments at different levels
# (e.g. in initialize()) or group() functions above the command to have the same names as
# the command's options. You can work around this by using a different name for the
# option in the command and supplying the desired name in the annotation, but its an odd
# quirk imposed by the base class for users to be aware of.


import inspect
import sys
import typing as t
from copy import copy, deepcopy
from importlib import import_module
from pathlib import Path
from types import MethodType, SimpleNamespace

import click
from click.shell_completion import CompletionItem
from django.core.management import get_commands
from django.core.management.base import BaseCommand, CommandError
from django.core.management.base import OutputWrapper as BaseOutputWrapper
from django.core.management.color import Style as ColorStyle
from django.db.models import Model
from django.utils.translation import gettext as _

from django_typer import patch

patch.apply()

from typer import Typer
from typer.core import MarkupMode
from typer.core import TyperCommand as CoreTyperCommand
from typer.core import TyperGroup as CoreTyperGroup
from typer.main import get_command as get_typer_command
from typer.main import get_params_convertors_ctx_param_name_from_function
from typer.models import Context as TyperContext
from typer.models import Default, DefaultPlaceholder

from .completers import ModelObjectCompleter
from .parsers import ModelObjectParser
from .types import (
    ForceColor,
    NoColor,
    PythonPath,
    Settings,
    SkipChecks,
    Traceback,
    Verbosity,
    Version,
)
from .utils import _command_context, get_usage_script, traceback_config, with_typehint

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


VERSION = (1, 0, 7)

__title__ = "Django Typer"
__version__ = ".".join(str(i) for i in VERSION)
__author__ = "Brian Kohan"
__license__ = "MIT"
__copyright__ = "Copyright 2023-2024 Brian Kohan"


__all__ = [
    "TyperCommand",
    "Context",
    "initialize",
    "command",
    "group",
    "get_command",
    "model_parser_completer",
]

P = ParamSpec("P")
R = t.TypeVar("R")


def model_parser_completer(
    model_cls: t.Type[Model],
    lookup_field: t.Optional[str] = None,
    case_insensitive: bool = False,
    help_field: t.Optional[str] = ModelObjectCompleter.help_field,
    query: t.Optional[ModelObjectCompleter.QueryBuilder] = None,
    limit: t.Optional[int] = ModelObjectCompleter.limit,
    distinct: bool = ModelObjectCompleter.distinct,
    on_error: t.Optional[ModelObjectParser.error_handler] = ModelObjectParser.on_error,
) -> t.Dict[str, t.Any]:
    """
    A factory function that returns a dictionary that can be used to specify
    a parser and completer for a typer.Option or typer.Argument. This is a
    convenience function that can be used to specify the parser and completer
    for a model object in one go.

    .. code-block:: python

        def handle(
            self,
            obj: t.Annotated[
                ModelClass,
                typer.Argument(
                    **model_parser_completer(ModelClass, 'field_name'),
                    help=_("Fetch objects by their field_names.")
                ),
            ]
        ):
            ...


    :param model_cls: the model class to use for lookup
    :param lookup_field: the field to use for lookup, by default the primary key
    :param case_insensitive: whether to perform case insensitive lookups and
        completions, default: False
    :param help_field: the field to use for help output in completion suggestions,
        by default no help will be provided
    :param query: a callable that will be used to build the query for completions,
        by default the query will be reasonably determined by the field type
    :param limit: the maximum number of completions to return, default: 50
    :param distinct: whether to filter out already provided parameters in the
        completion suggestions, True by default
    :param on_error: a callable that will be called if the parser lookup fails
        to produce a matching object - by default a CommandError will be raised
    """
    return {
        "parser": ModelObjectParser(
            model_cls,
            lookup_field,
            case_insensitive=case_insensitive,
            on_error=on_error,
        ),
        "shell_complete": ModelObjectCompleter(
            model_cls,
            lookup_field,
            case_insensitive=case_insensitive,
            help_field=help_field,
            query=query,
            limit=limit,
            distinct=distinct,
        ),
    }


def get_command(
    command_name: str,
    *subcommand: str,
    stdout: t.Optional[t.IO[str]] = None,
    stderr: t.Optional[t.IO[str]] = None,
    no_color: bool = False,
    force_color: bool = False,
) -> t.Union[BaseCommand, MethodType]:
    """
    Get a Django_ command by its name and instantiate it with the provided options. This
    will work for subclasses of BaseCommand_ as well as for :class:`~django_typer.TyperCommand`
    subclasses. If subcommands are listed for a :class:`~django_typer.TyperCommand`, the
    method that corresponds to the command name will be returned. This method may then be
    invoked directly. If no subcommands are listed the command instance will be returned.

    Using ``get_command`` to fetch a command instance and then invoking the instance as
    a callable is the preferred way to execute :class:`~django_typer.TyperCommand` commands
    from code. The arguments and options passed to the __call__ method of the command should
    be fully resolved to their expected parameter types before being passed to the command.
    The call_command_ interface also works, but arguments must be unparsed strings
    and options may be either strings or resolved parameter types. The following is more
    efficient than call_command_.

    .. code-block:: python

        basic = get_command('basic')
        result = basic(
            arg1,
            arg2,
            arg3=0.5,
            arg4=1
        )

    Subcommands may be retrieved by passing the subcommand names as additional arguments:

    .. code-block:: python

        divide = get_command('hierarchy', 'math', 'divide')
        result = divide(10, 2)

    :param command_name: the name of the command to get
    :param subcommand: the subcommand to get if any
    :param stdout: the stdout stream to use
    :param stderr: the stderr stream to use
    :param no_color: whether to disable color
    :param force_color: whether to force color
    :raises ModuleNotFoundError: if the command is not found
    :raises LookupError: if the subcommand is not found
    """
    module = import_module(
        f"{get_commands()[command_name]}.management.commands.{command_name}"
    )
    cmd = module.Command(
        stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color
    )
    if subcommand:
        method = cmd.get_subcommand(*subcommand).click_command._callback.__wrapped__
        return MethodType(method, cmd)  # return the bound method

    return cmd


def _common_options(
    version: Version = False,
    verbosity: Verbosity = 1,
    settings: Settings = "",
    pythonpath: PythonPath = None,
    traceback: Traceback = False,
    no_color: NoColor = False,
    force_color: ForceColor = False,
    skip_checks: SkipChecks = False,
) -> None:
    """
    Common django options.
    """


# cache common params to avoid this extra work on every command
# we cant resolve these at module scope because translations break it
_common_params: t.Sequence[t.Union[click.Argument, click.Option]] = []


def _get_common_params() -> t.Sequence[t.Union[click.Argument, click.Option]]:
    """Use typer to convert the common options to click options"""
    global _common_params
    if not _common_params:
        _common_params = get_params_convertors_ctx_param_name_from_function(
            _common_options
        )[0]
    return _common_params


COMMON_DEFAULTS = {
    key: value.default
    for key, value in inspect.signature(_common_options).parameters.items()
}


class _ParsedArgs(SimpleNamespace):  # pylint: disable=too-few-public-methods
    """
    Emulate the argparse.Namespace class so that we can pass the parsed arguments
    into the BaseCommand infrastructure in the way it expects.
    """

    def __init__(self, args: t.Sequence[t.Any], **kwargs):
        super().__init__(**kwargs)
        self.args = args
        self.traceback = kwargs.get("traceback", TyperCommand._traceback)

    def _get_kwargs(self):
        return {"args": self.args, **COMMON_DEFAULTS}


class Context(TyperContext):
    """
    An extension of the `click.Context <https://click.palletsprojects.com/api/#context>`_
    class that adds a reference to the :class:`~django_typer.TyperCommand` instance so that
    the Django_ command can be accessed from within click_ and Typer_ callbacks that take a
    context. This context also keeps track of parameters that were supplied to call_command_.
    """

    django_command: "TyperCommand"
    children: t.List["Context"]
    _supplied_params: t.Dict[str, t.Any]

    parent: "Context"

    class ParamDict(dict):
        """
        An extension of dict we use to block updates to parameters that were supplied
        when the command was invoked via call_command_. This complexity is introduced
        by the hybrid parsing and option passing inherent to call_command_.
        """

        supplied: t.Sequence[str]

        def __init__(self, *args, supplied: t.Sequence[str]):
            super().__init__(*args)
            self.supplied = supplied

        def __setitem__(self, key, value):
            if key not in self.supplied:
                super().__setitem__(key, value)

    @property
    def supplied_params(self) -> t.Dict[str, t.Any]:
        """
        Get the parameters that were supplied when the command was invoked via
        call_command_, only the root context has these.
        """
        if self.parent:
            return self.parent.supplied_params
        return getattr(self, "_supplied_params", {})

    def __init__(
        self,
        command: click.Command,  # pylint: disable=redefined-outer-name
        parent: t.Optional["Context"] = None,
        django_command: t.Optional["TyperCommand"] = None,
        supplied_params: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs,
    ):
        super().__init__(command, parent=parent, **kwargs)
        if supplied_params:
            self._supplied_params = supplied_params
        if django_command:
            self.django_command = django_command
        else:
            assert parent
            self.django_command = parent.django_command

        self.params = self.ParamDict(
            {**self.params, **self.supplied_params},
            supplied=list(self.supplied_params.keys()),
        )
        self.children = []
        if parent:
            parent.children.append(self)


class _DjangoAdapterMixin(with_typehint(CoreTyperGroup)):  # type: ignore[misc]
    """
    A mixin we use to add additional needed contextual awareness to click Commands
    and Groups.
    """

    context_class: t.Type[click.Context] = Context
    django_command: "TyperCommand"
    callback_is_method: bool = True

    class Converter:
        """
        Because of the way the BaseCommand forces parsing to be done in a separate
        first step, type casting of input strings to the correct types will have
        sometimes happened already. We use this class to avoid double type casting.

        An alternative approach might be to flag converted values - but there does
        not seem to be a good approach to do this given how deep in the click
        infrastructure the conversion happens.
        """

    def get_params(self, ctx: click.Context) -> t.List[click.Parameter]:
        """
        We override get_params to check to make sure that prompt_required is not set for parameters
        that have already been prompted for during the initial parse phase. We have to do this
        because of we're stuffing the click infrastructure into the django infrastructure and the
        django infrastructure forces a two step parse process whereas click does not easily support
        separating these.

        There may be a more sound approach than this?
        """
        modified = []
        params = super().get_params(ctx)
        for param in params:
            if (
                getattr(param, "prompt", None)
                and getattr(param, "prompt_required", False)
                and getattr(ctx, "supplied_params", {}).get(param.name, None)
            ):
                param = copy(param)
                setattr(param, "prompt_required", False)
                param.required = False
            modified.append(param)
        return modified

    def shell_complete(
        self, ctx: click.Context, incomplete: str
    ) -> t.List[CompletionItem]:
        """
        By default if the incomplete string is a space and there are no completions
        the click infrastructure will return _files. We'd rather return parameters
        for the command if there are any available.
        """
        completions = super().shell_complete(ctx, incomplete)
        if not completions and (incomplete.isspace() or not incomplete):
            completions = super().shell_complete(
                ctx, min(getattr(ctx, "_opt_prefixes", [""]))
            )
        return completions

    def common_params(self) -> t.Sequence[t.Union[click.Argument, click.Option]]:
        """
        Get the django common options that should be included in this click command.
        These will very depending on how the base class command is specified so look
        to individual implementations for details.
        """
        return []

    def __init__(
        self,
        *args,
        callback: t.Callable[..., t.Any],
        params: t.Optional[t.List[click.Parameter]] = None,
        **kwargs,
    ):
        params = params or []
        self._callback = callback
        expected = [param.name for param in params[1:] if param.name]
        self_arg = params[0].name if params and params[0].name else "self"

        def call_with_self(*args, **kwargs):
            ctx = t.cast(Context, click.get_current_context())
            return callback(
                *args,
                **{
                    # we could call param.process_value() here to allow named
                    # parameters to be passed as their unparsed string values,
                    # we don't because this forces some weird idempotency on custom
                    # parsers that might make errors more frequent for users and also
                    # this would be inconsistent with call_command behavior for BaseCommands
                    # which expect the parsed values to be passed by name. Unparsed values can
                    # always be passed as argument strings.
                    param: val
                    for param, val in kwargs.items()
                    if param in expected
                },
                **(
                    {self_arg: getattr(ctx, "django_command", None)}
                    if self.callback_is_method
                    else {}
                ),
            )

        super().__init__(
            *args,
            params=[
                *(params[1:] if self.callback_is_method else params),
                *[
                    param
                    for param in self.common_params()
                    if param.name not in expected
                ],
            ],
            callback=call_with_self,
            **kwargs,
        )


class TyperCommandWrapper(_DjangoAdapterMixin, CoreTyperCommand):
    """
    This class extends the TyperCommand class to work with the django-typer
    interfaces. If you need to add functionality to the command class - which
    you should not - you should inherit from this class.
    """

    def common_params(self) -> t.Sequence[t.Union[click.Argument, click.Option]]:
        """
        Return the common django params that are not suppressed only if the django
        command has a single command and no callback or other groups. When there are
        multiple commands and groups - the command parameters are added to a global
        initialization callback. See the meta class for details.
        """
        if (
            hasattr(self, "django_command")
            and self.django_command._num_commands < 2
            and not self.django_command._has_callback
            and not self.django_command._root_groups
        ):
            return [
                param
                for param in _get_common_params()
                if param.name
                and param.name
                not in (self.django_command.suppressed_base_arguments or [])
            ]
        return super().common_params()


class TyperGroupWrapper(_DjangoAdapterMixin, CoreTyperGroup):
    """
    This class extends the TyperGroup class to work with the django-typer
    interfaces. If you need to add functionality to the group class - which
    you should not - you should inherit from this class.
    """

    def common_params(self) -> t.Sequence[t.Union[click.Argument, click.Option]]:
        """
        Add the common parameters to this group only if this group is the root
        command's user specified initialize callback.
        """
        if (
            hasattr(self, "django_command") and self.django_command._has_callback
        ) or getattr(self, "common_init", False):
            return [
                param
                for param in _get_common_params()
                if param.name
                if param.name
                not in (self.django_command.suppressed_base_arguments or [])
            ]
        return super().common_params()


class GroupFunction(Typer):
    """
    Typer_ adds additional groups of commands by adding Typer_ apps to parent
    Typer_ apps. This class extends the ``typer.Typer`` class so that we can add
    the additional information necessary to attach this app to the root app
    and other groups specified on the django command.
    """

    bound: bool = False
    django_command_cls: t.Type["TyperCommand"]
    _callback: t.Callable[..., t.Any]

    def __get__(
        self, obj: t.Optional["TyperCommand"], _=None
    ) -> t.Union["GroupFunction", MethodType]:
        """
        Our Typer app wrapper also doubles as a descriptor, so when
        it is accessed on the instance, we return the wrapped function
        so it may be called directly - but when accessed on the class
        the app itself is returned so it can modified by other decorators
        on the class and subclasses.
        """
        if obj is None:
            return self
        return MethodType(self._callback, obj)

    def __init__(self, *args, **kwargs):
        self._callback = kwargs["callback"]
        super().__init__(*args, **kwargs)

    def bind(self, django_command_cls: t.Type["TyperCommand"]):
        """
        Bind this typer app to the given django command class. Only groups at
        root need to be bound - and will be done so by the meta class, this will
        happen automatically (See group()) when groups are added to other groups.
        """
        self.django_command_cls = django_command_cls
        # the deepcopy is necessary for instances where classes derive
        # from Command classes and replace/extend commands on groups
        # defined in the base class - this avoids the extending class
        # polluting the base class's command tree
        self.django_command_cls.typer_app.add_typer(deepcopy(self))

    def callback(self, *args, **kwargs):
        """
        callback is not supported because we've adapted the typer interface to be more
        intuitive for django users. The callback for a group is the function decorated
        by group().
        """
        raise NotImplementedError(
            _(
                "callback is not supported - the function decorated by group() is the "
                "callback."
            )
        )

    def command(  # type: ignore
        self,
        name: t.Optional[str] = None,
        *,
        cls: t.Type[CoreTyperCommand] = TyperCommandWrapper,
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = None,
        help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
        epilog: t.Optional[str] = None,
        short_help: t.Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        # Rich settings
        rich_help_panel: t.Union[str, None] = Default(None),
        **kwargs: t.Dict[str, t.Any],
    ) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
        """
        A function decorator that creates a new command and attaches it to this group.
        This is a passthrough to Typer.command() and the options are the same, except
        we swap the default command class for our wrapper.

        The decorated function is the command function. It may also be invoked directly
        as a method from an instance of the django command class.

        .. code-block:: python

            class Command(TyperCommand):

                @group()
                def group1(self):
                    pass

                @group1.command()
                def command1(self):
                    # do stuff here

        .. note::

            If you need to use a different command class you will need to either
            inherit from django-typer or make sure yours is interface compatible with
            our extensions. You shouldn't need to do this though - if the library does
            not do something you need it to please submit an issue.

        :param name: the name of the command (defaults to the name of the decorated
            function)
        :param cls: the command class to use
        :param context_settings: the context settings to use - see
            `click docs <https://click.palletsprojects.com/api/#context>`_.
        :param help: the help string to use, defaults to the function docstring, if
            you need the help to be translated you should use the help kwarg instead
            because docstrings will not be translated.
        :param epilog: the epilog to use in the help output
        :param short_help: the short help to use in the help output
        :param options_metavar: the metavar to use for options in the help output
        :param add_help_option: whether to add the help option to the command
        :param no_args_is_help: whether to show the help if no arguments are provided
        :param hidden: whether to hide the command from help output
        :param deprecated: show a deprecation warning
        :param rich_help_panel: the rich help panel to use - if rich is installed
            this can be used to group commands into panels in the help output.
        """

        def decorator(f: t.Callable[P, R]) -> t.Callable[P, R]:
            return super(  # pylint: disable=super-with-arguments
                GroupFunction, self
            ).command(
                name=name,
                cls=cls,
                context_settings=context_settings,
                help=help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                no_args_is_help=no_args_is_help,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
                **kwargs,
            )(
                f
            )

        return decorator

    def group(
        self,
        name: t.Optional[str] = Default(None),
        cls: t.Type[CoreTyperGroup] = TyperGroupWrapper,
        invoke_without_command: bool = Default(False),
        no_args_is_help: bool = Default(False),
        subcommand_metavar: t.Optional[str] = Default(None),
        chain: bool = Default(False),
        result_callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
        # Command
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = Default(None),
        help: t.Optional[str] = Default(None),  # pylint: disable=redefined-builtin
        epilog: t.Optional[str] = Default(None),
        short_help: t.Optional[str] = Default(None),
        options_metavar: str = Default("[OPTIONS]"),
        add_help_option: bool = Default(True),
        hidden: bool = Default(False),
        deprecated: bool = Default(False),
        # Rich settings
        rich_help_panel: t.Union[str, None] = Default(None),
        **kwargs: t.Dict[str, t.Any],
    ) -> t.Callable[[t.Callable[..., t.Any]], "GroupFunction"]:
        """
        Create a new subgroup and attach it to this group. This is like creating a new
        Typer app and adding it to a parent Typer app. The kwargs are passed through
        to the Typer() constructor.

        .. code-block:: python

            class Command(TyperCommand):

                @group()
                def group1(self):
                    pass

                @group1.group()
                def subgroup(self):
                    # do common group init stuff here

                @subgroup.command(help=_('My command does good stuff!'))
                def subcommand(self):
                    # do command stuff here


        :param name: the name of the group
        :param cls: the group class to use
        :param invoke_without_command: whether to invoke the group callback if no command was
            specified.
        :param no_args_is_help: whether to show the help if no arguments are provided
        :param subcommand_metavar: the metavar to use for subcommands in the help output
        :param chain: whether to chain commands, this allows multiple commands from the group
            to be specified and run in order sequentially in one call from the command line.
        :param result_callback: a callback to invoke with the result of the command
        :param context_settings: the click context settings to use - see
            `click docs <https://click.palletsprojects.com/api/#context>`_.
        :param help: the help string to use, defaults to the function docstring, if you need
            to translate the help you should use the help kwarg instead because docstrings
            will not be translated.
        :param epilog: the epilog to use in the help output
        :param short_help: the short help to use in the help output
        :param options_metavar: the metavar to use for options in the help output
        :param add_help_option: whether to add the help option to the command
        :param hidden: whether to hide this group from the help output
        :param deprecated: show a deprecation warning
        :param rich_help_panel: the rich help panel to use - if rich is installed
            this can be used to group commands into panels in the help output.
        """

        def create_app(func: t.Callable[..., t.Any]) -> GroupFunction:
            grp = GroupFunction(  # type: ignore
                name=name,
                cls=cls,
                invoke_without_command=invoke_without_command,
                no_args_is_help=no_args_is_help,
                subcommand_metavar=subcommand_metavar,
                chain=chain,
                result_callback=result_callback,
                callback=func,
                context_settings=context_settings,
                help=help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
                **kwargs,
            )
            self.add_typer(grp)
            grp.bound = True
            return grp

        return create_app


def initialize(
    name: t.Optional[str] = Default(None),
    *,
    cls: t.Type[TyperGroupWrapper] = TyperGroupWrapper,
    invoke_without_command: bool = Default(False),
    no_args_is_help: bool = Default(False),
    subcommand_metavar: t.Optional[str] = Default(None),
    chain: bool = Default(False),
    result_callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
    # Command
    context_settings: t.Optional[t.Dict[t.Any, t.Any]] = Default(None),
    help: t.Optional[str] = Default(None),  # pylint: disable=redefined-builtin
    epilog: t.Optional[str] = Default(None),
    short_help: t.Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs: t.Dict[str, t.Any],
) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
    """
    A function decorator that creates a Typer_
    `callback <https://typer.tiangolo.com/tutorial/commands/callback/>`_. This
    decorator wraps the
    `Typer.callback() <https://typer.tiangolo.com/tutorial/commands/callback/>`_
    functionality. We've renamed it to ``initialize()`` because ``callback()`` is
    to general and not intuitive. Callbacks in Typer_ are functions that are invoked
    before a command is invoked and that can accept their own arguments. When an
    ``initialize()`` function is supplied to a django :class:`~django_typer.TyperCommand`
    the default Django_ options will be added as parameters. You can specify these
    parameters (see :mod:`django_typer.types`) as arguments on the wrapped function
    if you wish to receive them - otherwise they will be intercepted by the base class
    infrastructure and used to their purpose.

    The parameters are passed through to
    `Typer.callback() <https://typer.tiangolo.com/tutorial/commands/callback/>`_

    For example the below command defines two subcommands that both have a common
    initializer that accepts a --precision parameter option:

    .. code-block:: python
        :linenos:
        :caption: management/commands/math.py

        import typing as t
        from typer import Argument, Option
        from django_typer import TyperCommand, initialize, command


        class Command(TyperCommand):

            precision = 2

            @initialize(help="Do some math at the given precision.")
            def init(
                self,
                precision: t.Annotated[
                    int, Option(help="The number of decimal places to output.")
                ] = precision,
            ):
                self.precision = precision

            @command(help="Multiply the given numbers.")
            def multiply(
                self,
                numbers: t.Annotated[
                    t.List[float], Argument(help="The numbers to multiply")
                ],
            ):
                ...

            @command()
            def divide(
                self,
                numerator: t.Annotated[float, Argument(help="The numerator")],
                denominator: t.Annotated[float, Argument(help="The denominator")]
            ):
                ...

    When we run, the command we should provide the --precision option before the subcommand:

        .. code-block:: bash

            $ ./manage.py math --precision 5 multiply 2 2.333
            4.66600

    :param name: the name of the callback (defaults to the name of the decorated
        function)
    :param cls: the command class to use - (the initialize() function is technically
        the root command group)
    :param invoke_without_command: whether to invoke the callback if no command was
        specified.
    :param no_args_is_help: whether to show the help if no arguments are provided
    :param subcommand_metavar: the metavar to use for subcommands in the help output
    :param chain: whether to chain commands, this allows multiple commands from the group
        to be specified and run in order sequentially in one call from the command line.
    :param result_callback: a callback to invoke with the result of the command
    :param context_settings: the click context settings to use - see
        `click docs <https://click.palletsprojects.com/api/#context>`_.
    :param help: the help string to use, defaults to the function docstring, if you need
        to translate the help you should use the help kwarg instead because docstrings
        will not be translated.
    :param epilog: the epilog to use in the help output
    :param short_help: the short help to use in the help output
    :param options_metavar: the metavar to use for options in the help output
    :param add_help_option: whether to add the help option to the command
    :param hidden: whether to hide this group from the help output
    :param deprecated: show a deprecation warning
    :param rich_help_panel: the rich help panel to use - if rich is installed
        this can be used to group commands into panels in the help output.
    """

    def decorator(func: t.Callable[P, R]) -> t.Callable[P, R]:
        setattr(
            func,
            "_typer_callback_",
            lambda cmd, _name=None, _help=Default(
                None
            ), **extra: cmd.typer_app.callback(
                name=name or _name,
                cls=type("_AdaptedCallback", (cls,), {"django_command": cmd}),
                invoke_without_command=invoke_without_command,
                subcommand_metavar=subcommand_metavar,
                chain=chain,
                result_callback=result_callback,
                context_settings=context_settings,
                help=cmd.typer_app.info.help or help or _help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                no_args_is_help=no_args_is_help,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
                **kwargs,
                **extra,
            )(
                func
            ),
        )
        return func

    return decorator


def command(  # pylint: disable=keyword-arg-before-vararg
    name: t.Optional[str] = None,
    *,
    cls: t.Type[TyperCommandWrapper] = TyperCommandWrapper,
    context_settings: t.Optional[t.Dict[t.Any, t.Any]] = None,
    help: t.Optional[str] = None,  # pylint: disable=redefined-builtin
    epilog: t.Optional[str] = None,
    short_help: t.Optional[str] = None,
    options_metavar: str = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs: t.Dict[str, t.Any],
) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
    """
    A function decorator that creates a new command and attaches it to the root
    command group. This is a passthrough to
    `Typer.command() <https://typer.tiangolo.com/tutorial/commands/>`_ and the
    options are the same, except we swap the default command class for our wrapper.

    We do not need to decorate handle() functions with this decorator, but if we
    want to pass options upstream to typer we can:

    .. code-block:: python

        class Command(TyperCommand):

            @command(epilog="This is the epilog for the command.")
            def handle(self):
                ...

    We can also use the command decorator to define multiple subcommands:

    .. code-block:: python

        class Command(TyperCommand):

            @command()
            def command1(self):
                # execute command1 logic here

            @command(name='command2')
            def other_command(self):
                # arguments passed to the decorator are passed to typer and control
                # various aspects of the command, for instance here we've changed the
                # name of the command to 'command2' from 'other_command'

    The decorated function is the command function. It may also be invoked directly
    as a method from an instance of the :class:`~django_typer.TyperCommand` class,
    see :func:`~django_typer.get_command`.

    :param name: the name of the command (defaults to the name of the decorated
        function)
    :param cls: the command class to use
    :param context_settings: the context settings to use - see
        `click docs <https://click.palletsprojects.com/api/#context>`_.
    :param help: the help string to use, defaults to the function docstring, if
        you need the help to be translated you should use the help kwarg instead
        because docstrings will not be translated.
    :param epilog: the epilog to use in the help output
    :param short_help: the short help to use in the help output
    :param options_metavar: the metavar to use for options in the help output
    :param add_help_option: whether to add the help option to the command
    :param no_args_is_help: whether to show the help if no arguments are provided
    :param hidden: whether to hide the command from help output
    :param deprecated: show a deprecation warning
    :param rich_help_panel: the rich help panel to use - if rich is installed
        this can be used to group commands into panels in the help output.
    """

    def decorator(func: t.Callable[P, R]) -> t.Callable[P, R]:
        setattr(
            func,
            "_typer_command_",
            lambda cmd, _name=None, _help=None, **extra: cmd.typer_app.command(
                name=name or _name,
                cls=type("_AdaptedCommand", (cls,), {"django_command": cmd}),
                context_settings=context_settings,
                help=help or _help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                no_args_is_help=no_args_is_help,
                hidden=hidden,
                deprecated=deprecated,
                # Rich settings
                rich_help_panel=rich_help_panel,
                **kwargs,
                **extra,
            )(func),
        )
        return func

    return decorator


def group(
    name: t.Optional[str] = Default(None),
    cls: t.Type[TyperGroupWrapper] = TyperGroupWrapper,
    invoke_without_command: bool = Default(False),
    no_args_is_help: bool = Default(False),
    subcommand_metavar: t.Optional[str] = Default(None),
    chain: bool = Default(False),
    result_callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
    # Command
    context_settings: t.Optional[t.Dict[t.Any, t.Any]] = Default(None),
    help: t.Optional[str] = Default(None),  # pylint: disable=redefined-builtin
    epilog: t.Optional[str] = Default(None),
    short_help: t.Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs: t.Dict[str, t.Any],
) -> t.Callable[[t.Callable[..., t.Any]], GroupFunction]:
    """
    A function decorator that creates a new subgroup and attaches it to the root
    command group. This is like creating a new Typer_ app and adding it to a parent
    Typer app. The kwargs are passed through to the Typer() constructor. The group()
    functions work like :func:`~django_typer.initialize` functions for their command
    groups.

    .. code-block:: python
        :caption: management/commands/example.py

        from django_typer import TyperCommand, group

        class Command(TyperCommand):

            @group()
            def group1(self, flag: bool = False):
                # do group init stuff here

            # to attach a command to the group, use the command() decorator
            # on the group function
            @group1.command()
            def command1(self):
                ...

            # you can also attach subgroups to groups!
            @group1.group()
            def subgroup(self):
                # do subgroup init stuff here

            @subgroup.command()
            def subcommand(self):
                ...

    These groups and subcommands can be invoked from the command line like so:

    .. code-block:: bash

        $ ./manage.py example group1 --flag command1
        $ ./manage.py example group1 --flag subgroup subcommand

    :param name: the name of the group (defaults to the name of the decorated function)
    :param cls: the group class to use
    :param invoke_without_command: whether to invoke the group callback if no command
        was specified.
    :param no_args_is_help: whether to show the help if no arguments are provided
    :param subcommand_metavar: the metavar to use for subcommands in the help output
    :param chain: whether to chain commands, this allows multiple commands from the group
        to be specified and run in order sequentially in one call from the command line.
    :param result_callback: a callback to invoke with the result of the command
    :param context_settings: the click context settings to use - see
        `click docs <https://click.palletsprojects.com/api/#context>`_.
    :param help: the help string to use, defaults to the function docstring, if you need
        to translate the help you should use the help kwarg instead because docstrings
        will not be translated.
    :param epilog: the epilog to use in the help output
    :param short_help: the short help to use in the help output
    :param options_metavar: the metavar to use for options in the help output
    :param add_help_option: whether to add the help option to the command
    :param hidden: whether to hide this group from the help output
    :param deprecated: show a deprecation warning
    :param rich_help_panel: the rich help panel to use - if rich is installed
        this can be used to group commands into panels in the help output.
    """

    def create_app(func: t.Callable[..., t.Any]) -> GroupFunction:
        grp = GroupFunction(  # type: ignore
            name=name,
            cls=cls,
            invoke_without_command=invoke_without_command,
            no_args_is_help=no_args_is_help,
            subcommand_metavar=subcommand_metavar,
            chain=chain,
            result_callback=result_callback,
            callback=func,
            context_settings=context_settings,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            hidden=hidden,
            deprecated=deprecated,
            rich_help_panel=rich_help_panel,
            **kwargs,
        )
        return grp

    return create_app


class TyperCommandMeta(type):
    """
    The metaclass used to build the TyperCommand class. This metaclass is responsible
    for building Typer app using the arguments supplied to the TyperCommand constructor.
    It also discovers if handle() was supplied as the single command implementation.

    .. warning::

        This metaclass is private because it may change substantially in the future to
        support changes in the upstream libraries. The TyperCommand interface should be
        considered the stable interface.

    :param name: the name of the class being created
    :param bases: the base classes of the class being created
    :param attrs: the attributes of the class being created
    :param cls: The class to use as the core typer group wrapper
    :param invoke_without_command: whether to invoke the group callback if no command
        was specified.
    :param no_args_is_help: whether to show the help if no arguments are provided
    :param subcommand_metavar: the metavar to use for subcommands in the help output
    :param chain: whether to chain commands, this allows multiple commands from the group
        to be specified and run in order sequentially in one call from the command line.
    :param result_callback: a callback to invoke with the result of the command
    :param context_settings: the click context settings to use - see
        `click docs <https://click.palletsprojects.com/api/#context>`_.
    :param help: the help string to use, defaults to the function docstring, if you need
        to translate the help you should use the help kwarg instead because docstrings
        will not be translated.
    :param epilog: the epilog to use in the help output
    :param short_help: the short help to use in the help output
    :param options_metavar: the metavar to use for options in the help output
    :param add_help_option: whether to add the help option to the command
    :param hidden: whether to hide this group from the help output
    :param deprecated: show a deprecation warning
    :param rich_markup_mode: the rich markup mode to use - if rich is installed
        this can be used to enable rich markup or Markdown in the help output. Can
        be "markdown", "rich" or None to disable markup rendering.
    :param rich_help_panel: the rich help panel to use - if rich is installed
        this can be used to group commands into panels in the help output.
    :param pretty_exceptions_enable: whether to enable pretty exceptions - if rich is
        installed this can be used to enable pretty exception rendering. This will
        default to on if the traceback configuration settings installs the rich
        traceback handler. This allows tracebacks to be configured by the user on a
        per deployment basis in the settings file. We therefore do not advise
        hardcoding this value.
    :param pretty_exceptions_show_locals: whether to show local variables in pretty
        exceptions - if rich is installed. This will default to the 'show_locals'
        setting in the traceback configuration setting (on by default). This allows
        tracebacks to be configured by the user on a per deployment basis in the
        settings file. We therefore do not advise hardcoding this value.
    :param pretty_exceptions_short: whether to show short tracebacks in pretty
        exceptions - if rich is installed. This will default to the 'short' setting
        in the traceback configuration setting (off by default). This allows tracebacks
        to be configured by the user on a per deployment basis in the settings file. We
        therefore do not advise hardcoding this value.
    """

    style: ColorStyle
    stdout: t.IO[str]
    stderr: t.IO[str]
    requires_system_checks: t.Union[t.Sequence[str], str]
    suppressed_base_arguments: t.Optional[t.Iterable[str]]
    typer_app: Typer
    no_color: bool
    force_color: bool
    _num_commands: int = 0
    _has_callback: bool = False
    _root_groups: int = 0
    _handle: t.Optional[t.Callable[..., t.Any]]

    def __new__(
        mcs,
        name,
        bases,
        attrs,
        cls: t.Optional[t.Type[CoreTyperGroup]] = TyperGroupWrapper,
        invoke_without_command: bool = Default(False),
        no_args_is_help: bool = Default(False),
        subcommand_metavar: t.Optional[str] = Default(None),
        chain: bool = Default(False),
        result_callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = Default(None),
        callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
        help: t.Optional[str] = Default(None),  # pylint: disable=redefined-builtin
        epilog: t.Optional[str] = Default(None),
        short_help: t.Optional[str] = Default(None),
        options_metavar: str = Default("[OPTIONS]"),
        add_help_option: bool = Default(True),
        hidden: bool = Default(False),
        deprecated: bool = Default(False),
        rich_markup_mode: MarkupMode = None,
        rich_help_panel: t.Union[str, None] = Default(None),
        pretty_exceptions_enable: t.Union[DefaultPlaceholder, bool] = Default(True),
        pretty_exceptions_show_locals: t.Union[DefaultPlaceholder, bool] = Default(
            True
        ),
        pretty_exceptions_short: t.Union[DefaultPlaceholder, bool] = Default(True),
    ):
        """
        This method is called when a new class is created.
        """
        try:
            # avoid unnecessary work creating the TyperCommand class
            # is there a less weird way to do this?
            is_base_init = not TyperCommand
        except NameError:
            is_base_init = True
        typer_app = None

        if not is_base_init:
            # conform the pretty exception defaults to the settings traceback config
            tb_config = traceback_config()
            if isinstance(pretty_exceptions_enable, DefaultPlaceholder):
                pretty_exceptions_enable = isinstance(tb_config, dict)

            tb_config = tb_config if isinstance(tb_config, dict) else {}
            if isinstance(pretty_exceptions_show_locals, DefaultPlaceholder):
                pretty_exceptions_show_locals = tb_config.get(
                    "show_locals", pretty_exceptions_show_locals
                )
            if isinstance(pretty_exceptions_short, DefaultPlaceholder):
                pretty_exceptions_short = tb_config.get(
                    "short", pretty_exceptions_short
                )

            typer_app = Typer(
                name=mcs.__module__.rsplit(".", maxsplit=1)[-1],
                cls=cls,
                help=help or attrs.get("help", Default(None)),
                invoke_without_command=invoke_without_command,
                no_args_is_help=no_args_is_help,
                subcommand_metavar=subcommand_metavar,
                chain=chain,
                result_callback=result_callback,
                context_settings=context_settings,
                callback=callback,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                hidden=hidden,
                deprecated=deprecated,
                add_completion=False,  # see autocomplete command instead!
                rich_markup_mode=rich_markup_mode,
                rich_help_panel=rich_help_panel,
                pretty_exceptions_enable=pretty_exceptions_enable,
                pretty_exceptions_show_locals=t.cast(
                    bool, pretty_exceptions_show_locals
                ),
                pretty_exceptions_short=t.cast(bool, pretty_exceptions_short),
            )

            attrs = {
                "_handle": attrs.pop("handle", None),
                **attrs,
                "typer_app": typer_app,
            }

        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **kwargs):
        """
        This method is called after a new class is created.
        """
        if getattr(cls, "typer_app", None):
            cls.typer_app.info.name = cls.__module__.rsplit(".", maxsplit=1)[-1]
            cls.suppressed_base_arguments = {
                arg.lstrip("--").replace("-", "_")
                for arg in cls.suppressed_base_arguments or []
            }  # per django docs - allow these to be specified by either the option or param name

            def get_ctor(attr: t.Any) -> t.Optional[t.Callable[..., t.Any]]:
                return getattr(
                    attr, "_typer_command_", getattr(attr, "_typer_callback_", None)
                )

            # because we're mapping a non-class based interface onto a class based
            # interface, we have to handle this class mro stuff manually here
            for cmd_cls, cls_attrs in [
                *[(base, vars(base)) for base in reversed(bases)],
                (cls, attrs),
            ]:
                if not issubclass(cmd_cls, TyperCommand) or cmd_cls is TyperCommand:
                    continue
                for attr in [*cls_attrs.values(), cls._handle]:
                    cls._num_commands += hasattr(attr, "_typer_command_")
                    cls._has_callback |= hasattr(attr, "_typer_callback_")
                    if isinstance(attr, GroupFunction) and not attr.bound:
                        attr.bind(cls)  # type: ignore
                        cls._root_groups += 1

                if cmd_cls._handle:
                    ctor = get_ctor(cmd_cls._handle)
                    if ctor:
                        ctor(
                            cls,
                            _name=cls.typer_app.info.name,
                            _help=getattr(cls, "help", None),
                        )
                    else:
                        cls._num_commands += 1
                        cls.typer_app.command(
                            cls.typer_app.info.name,
                            cls=type(
                                "_AdaptedCommand",
                                (TyperCommandWrapper,),
                                {"django_command": cls},
                            ),
                            help=cls.typer_app.info.help or None,
                        )(cmd_cls._handle)

                for attr in cls_attrs.values():
                    (get_ctor(attr) or (lambda _: None))(cls)

            if (
                cls._num_commands > 1 or cls._root_groups > 0
            ) and not cls.typer_app.registered_callback:
                cls.typer_app.callback(
                    cls=type(
                        "_AdaptedCallback",
                        (TyperGroupWrapper,),
                        {
                            "django_command": cls,
                            "callback_is_method": False,
                            "common_init": True,
                        },
                    )
                )(lambda: None)

        super().__init__(name, bases, attrs, **kwargs)


class CommandNode:
    """
    A tree node that represents a command in the command tree. This is used to
    walk the click command hierarchy and produce helps and map command paths
    to command functions. The command tree is built on TyperCommand initialization.

    :param name: the name of the command or subcommand
    :param click_command: the click command object
    :param context: the click context object
    :param django_command: the django command instance
    :param parent: the parent node or None if this is a root node
    """

    name: str
    click_command: click.Command
    context: TyperContext
    django_command: "TyperCommand"
    parent: t.Optional["CommandNode"] = None
    children: t.Dict[str, "CommandNode"]

    def __init__(
        self,
        name: str,
        click_command: click.Command,
        context: TyperContext,
        django_command: "TyperCommand",
        parent: t.Optional["CommandNode"] = None,
    ):
        self.name = name
        self.click_command = click_command
        self.context = context
        self.django_command = django_command
        self.parent = parent
        self.children = {}

    def print_help(self) -> t.Optional[str]:
        """
        Prints the help for this command to stdout of the django command.
        """
        # if rich is installed this prints the help, if it is not it
        # returns the help as a string - we deal with this higher on the
        # stack
        return self.click_command.get_help(self.context)

    def get_command(self, *command_path: str) -> "CommandNode":
        """
        Return the command node for the given command path at or below
        this node.

        :param command_path: the path(s) to the command to retrieve
        :return: the command node at the given path
        :raises LookupError: if the command path does not exist
        """
        if not command_path:
            return self
        try:
            return self.children[command_path[0]].get_command(*command_path[1:])
        except KeyError as err:
            raise LookupError(f'No such command "{command_path[0]}"') from err


class TyperParser:
    """
    A class that conforms to the argparse.ArgumentParser interface that the django
    base class works with that is returned by BaseCommand.create_parser(). This class
    does not strictly conform to the argparse interface but does just enough to
    satisfy the django base class.

    :param django_command: the django command instance
    :param prog_name: the name of the manage script that invoked the command
    :param subcommand: the name of the django command
    """

    class Action:
        """
        Emulate the interface of argparse.Action. Partial implementation
        used to satisfy the django BaseCommand class.

        :param param: the click parameter to wrap as an argparse Action
        """

        param: click.Parameter
        required: bool = False

        def __init__(self, param: click.Parameter):
            self.param = param

        @property
        def dest(self) -> t.Optional[str]:
            """
            The name of the parameter as passed to the command.
            """
            return self.param.name

        @property
        def nargs(self) -> int:
            """
            The number of arguments consumed by this parameter or 0 if it is a flag.
            """
            return 0 if getattr(self.param, "is_flag", False) else self.param.nargs

        @property
        def option_strings(self) -> t.List[str]:
            """
            The list of allowable command line option strings for this parameter.
            """
            return list(self.param.opts) if isinstance(self.param, click.Option) else []

    _actions: t.List[t.Any]
    _mutually_exclusive_groups: t.List[t.Any] = []

    django_command: "TyperCommand"
    prog_name: str
    subcommand: str

    def __init__(self, django_command: "TyperCommand", prog_name, subcommand):
        self._actions = []
        self.django_command = django_command
        self.prog_name = prog_name
        self.subcommand = subcommand

        def populate_params(node: CommandNode) -> None:
            for param in node.click_command.params:
                self._actions.append(self.Action(param))
            for child in node.children.values():
                populate_params(child)

        populate_params(self.django_command.command_tree)

    def print_help(self, *command_path: str):
        """
        Print the help for the given command path to stdout of the django command.
        """
        self.django_command.command_tree.context.info_name = (
            f"{self.prog_name} {self.subcommand}"
        )
        command_node = self.django_command.get_subcommand(*command_path)
        hlp = command_node.print_help()
        if hlp:
            self.django_command.stdout.write(
                hlp, style_func=lambda msg: msg, ending="\n\n"
            )

    def parse_args(self, args=None, namespace=None) -> _ParsedArgs:
        """
        Parse the given arguments into a parsed arguments namespace object.
        If any arguments trigger termination of the command (like --help) then
        this method will exit the program.

        Parse will also add the common django parameter defaults to the parsed
        arguments object.

        :param args: the arguments to parse
        :param namespace: the namespace to populate with the parsed arguments
            (this is ignored for TyperCommands but is required by the django
            base class)
        """
        with self.django_command:
            cmd = get_typer_command(self.django_command.typer_app)
            with cmd.make_context(
                info_name=f"{self.prog_name} {self.subcommand}",
                django_command=self.django_command,
                args=list(args or []),
            ) as ctx:
                common = {**COMMON_DEFAULTS, **ctx.params}
                self.django_command._traceback = common.get(
                    "traceback", self.django_command._traceback
                )
                return _ParsedArgs(args=args or [], **common)

    def add_argument(self, *args, **kwargs):
        """
        add_argument() is disabled for TyperCommands because all arguments
        and parameters are specified as args and kwargs on the function calls.
        """
        raise NotImplementedError(_("add_argument() is not supported"))


class OutputWrapper(BaseOutputWrapper):
    """
    Override django's base OutputWrapper to avoid exceptions when strings are
    returned from command functions.
    """

    def write(self, msg="", style_func=None, ending=None):
        """
        If the message is not a string, first cast it before invoking the base
        class write method.
        """
        if not isinstance(msg, str):
            msg = str(msg)
        return super().write(msg=msg, style_func=style_func, ending=ending)


class TyperCommand(BaseCommand, metaclass=TyperCommandMeta):
    """
    An extension of BaseCommand_ that uses the Typer_ library to parse
    arguments_ and options_. This class adapts BaseCommand_ using a light touch
    that relies on most of the original BaseCommand_ implementation to handle
    default arguments and behaviors.

    All of the documented BaseCommand_ functionality works as expected. call_command_
    also works as expected. TyperCommands however add a few extra features:

        - We define arguments_ and options_ using concise and optionally annotated type hints.
        - Simple TyperCommands implemented only using handle() can be called directly
          by invoking the command as a callable.
        - We can define arbitrarily complex subcommand group hierarchies using the
          :func:`~django_typer.group` and :func:`~django_typer.command` decorators.
        - Commands and subcommands can be fetched and invoked directly as functions using
          :func:`~django_typer.get_command`
        - We can define common initialization logic for groups of commands using
          :func:`~django_typer.initialize`
        - TyperCommands may safely return non-string values from handle()

    Defining a typer command is a lot like defining a BaseCommand_ except that we do not
    have an add_arguments() method. Instead we define the parameters using type hints
    directly on handle():

    .. code-block:: python

        import typing as t
        from django_typer import TyperCommand

        class Command(TyperCommand):

            def handle(
                self,
                arg: str,
                option: t.Optional[str] = None
            ):
                # do command logic here

    TyperCommands can be extremely simple like above, or we can create really complex
    command group hierarchies with subcommands and subgroups (see :func:`~django_typer.group`
    and :func:`~django_typer.command`).

    Typer_ apps can be configured with a number of parameters to control behavior such as
    exception behavior, help output, help markup interpretation, result processing and
    execution flow. These parameters can be passed to typer as keyword arguments in your
    Command class inheritance:

    .. code-block:: python
        :caption: management/commands/chain.py
        :linenos:

        import typing as t
        from django_typer import TyperCommand, command


        class Command(TyperCommand, rich_markup_mode='markdown', chain=True):

            suppressed_base_arguments = [
                '--verbosity', '--traceback', '--no-color', '--force-color',
                '--skip_checks', '--settings', '--pythonpath', '--version'
            ]

            @command()
            def command1(self, option: t.Optional[str] = None):
                \"""This is a *markdown* help string\"""
                print('command1')
                return option

            @command()
            def command2(self, option: t.Optional[str] = None):
                \"""This is a *markdown* help string\"""
                print('command2')
                return option


    We're doing a number of things here:

        - Using the :func:`~django_typer.command` decorator to define multiple subcommands.
        - Using the `suppressed_base_arguments attribute
          <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand.suppressed_base_arguments>`_
          to suppress the default options Django adds to the command interface.
        - Using the `rich_markup_mode parameter
          <https://typer.tiangolo.com/tutorial/commands/help/#rich-markdown-and-markup>`_ to enable
          markdown rendering in help output.
        - Using the chain parameter to enable `command chaining
          <https://click.palletsprojects.com/commands/#multi-command-chaining>`_.


    We can see that our help renders like so:

    .. typer:: django_typer.tests.test_app.management.commands.chain.Command:typer_app
        :prog: ./manage.py chain
        :width: 80
        :convert-png: latex


    And we can see the chain behavior by calling our command(s) like so:

    .. code-block:: bash

        $ ./manage.py chain command1 --option one command2 --option two
        command1
        command2
        ['one', 'two']

    See :class:`~django_typer.TyperCommandMeta` for the list of accepted parameters. Also
    refer to the Typer_ docs for more information on the behaviors expected for
    those parameters - they are passed through to the Typer class constructor. Not all
    parameters may make sense in the context of a django command.

    :param stdout: the stdout stream to use
    :param stderr: the stderr stream to use
    :param no_color: whether to disable color output
    :param force_color: whether to force color output even if the stream is not a tty
    """

    # TyperCommands are built in stages. The metaclass is responsible for finding
    # all the commands and callbacks and building the Typer_ app. This happens at
    # class definition time (i.e. on module load). When the TyperCommand is instantiated
    # the command tree is built thats used for subcommand resolution in django-typer's
    # get_command method and for help output.

    style: ColorStyle
    stdout: BaseOutputWrapper
    stderr: BaseOutputWrapper
    # requires_system_checks: t.Union[t.List[str], t.Tuple[str, ...], t.Literal['__all__']]

    # we do not use verbosity because the base command does not do anything with it
    # if users want to use a verbosity flag like the base django command adds
    # they can use the type from django_typer.types.Verbosity
    suppressed_base_arguments = {"verbosity"}

    missing_args_message = "Missing parameter: {parameter}"

    typer_app: Typer
    no_color: bool = False
    force_color: bool = False
    _num_commands: int = 0
    _has_callback: bool = False
    _root_groups: int = 0
    _handle: t.Callable[..., t.Any]
    _traceback: bool = False

    command_tree: CommandNode

    @property
    def _name(self) -> str:
        """The name of the django command"""
        return self.typer_app.info.name or self.__module__.rsplit(".", maxsplit=1)[-1]

    def __enter__(self):
        _command_context.__dict__.setdefault("stack", []).append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _command_context.stack.pop()
        if isinstance(exc_val, click.exceptions.Exit):
            sys.exit(exc_val.exit_code)
        if isinstance(exc_val, click.exceptions.UsageError):
            err_msg = (
                _(self.missing_args_message).format(
                    parameter=getattr(getattr(exc_val, "param", None), "name", "")
                )
                if isinstance(exc_val, click.exceptions.MissingParameter)
                else str(exc_val)
            )

            # we might be in a subcommand - so make sure we pull that help out
            # by walking up the context tree until we're at root
            cmd_pth: t.List[str] = []
            ctx = exc_val.ctx
            while ctx and ctx.parent:
                assert ctx.info_name
                cmd_pth.insert(0, ctx.info_name)
                ctx = ctx.parent
            if (
                getattr(self, "_called_from_command_line", False)
                and not self._traceback
            ):
                self.print_help(sys.argv[0], self._name, *cmd_pth)
                self.stderr.write(err_msg)
                sys.exit(1)
            raise CommandError(str(exc_val)) from exc_val

    def __init__(
        self,
        stdout: t.Optional[t.TextIO] = None,
        stderr: t.Optional[t.TextIO] = None,
        no_color: bool = no_color,
        force_color: bool = force_color,
        **kwargs: t.Dict[str, t.Any],
    ):
        self.force_color = force_color
        self.no_color = no_color
        with self:
            super().__init__(
                stdout=stdout,
                stderr=stderr,
                no_color=no_color,
                force_color=force_color,
                **kwargs,
            )
            # redo output pipes to use our wrappers that avoid
            # exceptions when strings are returned from command functions
            stdout_style_func = self.stdout.style_func
            stderr_style_func = self.stderr.style_func
            self.stdout = OutputWrapper(stdout or sys.stdout)
            self.stderr = OutputWrapper(stderr or sys.stderr)
            self.stdout.style_func = stdout_style_func
            self.stderr.style_func = stderr_style_func
            self.command_tree = self._build_cmd_tree(get_typer_command(self.typer_app))

    def get_subcommand(self, *command_path: str) -> CommandNode:
        """Get the CommandNode"""
        return self.command_tree.get_command(*command_path)

    def _filter_commands(
        self, ctx: TyperContext, cmd_filter: t.Optional[t.List[str]] = None
    ):
        """
        Fetch subcommand names. Given a click context, return the list of commands
        that are valid return the list of commands that are valid for the given
        context.

        :param ctx: the click context
        :param cmd_filter: a list of command names to filter by, if None no subcommands
            will be filtered out
        :return: the list of command names that are valid for the given context
        """
        return sorted(
            [
                cmd
                for name, cmd in getattr(
                    ctx.command,
                    "commands",
                    {
                        name: ctx.command.get_command(ctx, name)  # type: ignore[attr-defined]
                        for name in (
                            ctx.command.list_commands(ctx)
                            if isinstance(ctx.command, click.MultiCommand)
                            else []
                        )
                    },
                ).items()
                if not cmd_filter or name in cmd_filter
            ],
            key=lambda item: item.name,
        )

    def _build_cmd_tree(
        self,
        cmd: click.Command,
        parent: t.Optional[Context] = None,
        info_name: t.Optional[str] = None,
        node: t.Optional[CommandNode] = None,
    ):
        """
        Recursively build the CommandNode tree used to walk the click command
        hierarchy.

        :param cmd: the click command to build the tree from
        :param parent: the parent click context
        :param info_name: the name of the command
        :param node: the parent node or None if this is a root node
        """
        assert cmd.name
        ctx = Context(cmd, info_name=info_name, parent=parent, django_command=self)
        current = CommandNode(cmd.name, cmd, ctx, self, parent=node)
        if node:
            node.children[cmd.name] = current
        for sub_cmd in self._filter_commands(ctx):
            self._build_cmd_tree(
                sub_cmd, parent=ctx, info_name=sub_cmd.name, node=current
            )
        return current

    def __init_subclass__(cls, **_):
        """Avoid passing typer arguments up the subclass init chain"""
        return super().__init_subclass__()

    def create_parser(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, prog_name: str, subcommand: str, **_
    ):
        """
        Create a parser for this command. This also sets the command
        context, so any functions below this call on the stack may
        use get_current_command() to retrieve the django command instance.

        :param prog_name: the name of the manage script that invoked the command
        :param subcommand: the name of the django command
        """
        with self:
            if getattr(self, "_called_from_command_line", False):
                script = get_usage_script(prog_name)
                if isinstance(script, Path):
                    prog_name = str(script)
                    if not str(prog_name).startswith(("..", "/", ".")):
                        prog_name = f"./{prog_name}"
                else:
                    prog_name = str(script)

            return TyperParser(self, prog_name, subcommand)

    def print_help(self, prog_name: str, subcommand: str, *cmd_path: str):
        """
        Print the help message for this command to stdout of the django command.

        :param prog_name: the name of the manage script that invoked the command
        :param subcommand: the name of the django command
        :param cmd_path: the path to the command to print the help for. This is
            an extension to the pase class print_help() interface, required because
            typer/click have different helps for each subgroup or subcommand.
        """
        with self:
            self.create_parser(prog_name, subcommand).print_help(*cmd_path)

    def __call__(self, *args, **kwargs):
        """
        Call this command's derived class handle() implementation directly. Note this
        does not call the handle() function below - but the handle() function that
        was implemented on the deriving class if one exists.

        When simple commands are implemented using only the handle() function we may
        invoke that handle function directly using this call operator:

        .. code-block:: python

            class Command(TyperCommand):

                def handle(self, option1: bool, option2: bool):
                    # invoked by this __call__

            my_command = get_command('my_command')

            # invoke the handle() function directly
            my_command(option1=True, option2=False)

        .. note::

            This only works for commands that implement handle(). Commands that have
            multiple commands and groups are not required to implement handle() and
            for those commands the functions should be invoked directly.

        :param args: the arguments to directly pass to handle()
        :param kwargs: the options to directly pass to handle()
        """
        with self:
            if getattr(self, "_handle", None) and callable(self._handle):
                return self._handle(*args, **kwargs)
            raise NotImplementedError(
                _(
                    "{cls} does not implement handle(), you must call the other command "
                    "functions directly."
                ).format(cls=self.__class__)
            )

    def handle(self, *args, **options):
        """
        Invoke the underlying Typer app with the given arguments and parameters.

        :param args: the arguments to pass to the command, may be strings needing
            to be parsed, or already resolved object types the argument ultimately
            resolves to. TODO - check this is true
        :param options: the options to pass to the command, may be strings needing
            to be parsed, or already resolved object types the option ultimately
            resolves to.
        :return: Any object returned by the Typer app
        """
        with self:
            return self.typer_app(
                args=args,
                standalone_mode=False,
                supplied_params=options,
                django_command=self,
                complete_var=None,
                prog_name=f"{sys.argv[0]} {self.typer_app.info.name}",
            )

    def run_from_argv(self, argv):
        """
        Wrap the BaseCommand.run_from_argv() method to push the command
        onto the stack so any code in frames below this can get a reference
        to the command instance using get_current_command().

        :param argv: the arguments to pass to the command
        """
        with self:
            return super().run_from_argv(argv)

    def execute(self, *args, **options):
        """
        Wrap the BaseCommand.execute() method to set and unset
        no_color and force_color options.

        This function pushes the command onto the stack so any frame
        below this call may use get_current_command() to get a reference
        to the command instance.

        args and options are passed to handle().

        :param args: the arguments to pass to the command
        :param options: the options to pass to the command
        :return: Any object returned by the command
        """
        no_color = self.no_color
        force_color = self.force_color
        if options.get("no_color", None) is not None:
            self.no_color = options["no_color"]
        if options.get("force_color", None) is not None:
            self.force_color = options["force_color"]
        try:
            with self:
                return super().execute(*args, **options)
        finally:
            self.no_color = no_color
            self.force_color = force_color
