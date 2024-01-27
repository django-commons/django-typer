r"""
    ___ _                           _____                       
   /   (_) __ _ _ __   __ _  ___   /__   \_   _ _ __   ___ _ __ 
  / /\ / |/ _` | '_ \ / _` |/ _ \    / /\/ | | | '_ \ / _ \ '__|
 / /_//| | (_| | | | | (_| | (_) |  / /  | |_| | |_) |  __/ |   
/___,'_/ |\__,_|_| |_|\__, |\___/   \/    \__, | .__/ \___|_|   
     |__/             |___/               |___/|_|              

"""

import contextlib
import inspect
import sys
import typing as t
from copy import deepcopy
from importlib import import_module
from types import MethodType, SimpleNamespace

import click
from click.shell_completion import CompletionItem
from django.conf import settings
from django.core.management import get_commands
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.utils.functional import lazy
from django.utils.translation import gettext as _
from typer import Typer
from typer.core import TyperCommand as CoreTyperCommand
from typer.core import TyperGroup as CoreTyperGroup
from typer.main import MarkupMode
from typer.main import get_command as get_typer_command
from typer.main import get_params_convertors_ctx_param_name_from_function
from typer.models import CommandFunctionType
from typer.models import Context as TyperContext
from typer.models import Default, DefaultPlaceholder

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

VERSION = (0, 4, "0b")

__title__ = "Django Typer"
__version__ = ".".join(str(i) for i in VERSION)
__author__ = "Brian Kohan"
__license__ = "MIT"
__copyright__ = "Copyright 2023 Brian Kohan"


__all__ = ["TyperCommand", "Context", "initialize", "command", "group", "get_command"]

"""
TODO
- useful django types (app label, etc)
- documentation
- linting
- type hints

design decision: no monkey-patching for call_command. call_command converts arguments to
strings. This is unavoidable and will just be a noted caveat that is also consistent with
how native django commands work. For calls with previously resolved types - the direct
callbacks should be invoked - either Command() or Command.group(). call_command however
*requires* options to be passed by value instead of by string. This should be fixed.

behavior should align with native django commands
"""

# try:
#     from typer import rich_utils
#     def get_color_system(default):
#         return None
#         ctx = click.get_current_context(silent=True)
#         if ctx:
#             return None if ctx.django_command.style == no_style() else default
#         return default

#     COLOR_SYSTEM = lazy(get_color_system, str)
#     rich_utils.COLOR_SYSTEM = COLOR_SYSTEM(rich_utils.COLOR_SYSTEM)
# except ImportError:
#     pass


def traceback_config() -> t.Union[bool, t.Dict[str, t.Any]]:
    """
    Fetch the rich traceback installation parameters from our settings. By default
    rich tracebacks are on with show_locals = True. If the config is set to False
    or None rich tracebacks will not be installed even if the library is present.

    This allows us to have a common traceback configuration for all commands. If rich
    tracebacks are managed separately this setting can also be switched off.
    """
    cfg = getattr(settings, "DT_RICH_TRACEBACK_CONFIG", {"show_locals": True})
    if cfg:
        return {"show_locals": True, **cfg}
    return bool(cfg)


def get_command(
    command_name: str,
    *subcommand: str,
    stdout: t.Optional[t.IO[str]] = None,
    stderr: t.Optional[t.IO[str]] = None,
    no_color: bool = False,
    force_color: bool = False,
):
    module = import_module(
        f"{get_commands()[command_name]}.management.commands.{command_name}"
    )
    cmd = module.Command(
        stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color
    )
    if subcommand:
        method = cmd.get_subcommand(*subcommand).command._callback.__wrapped__
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
):
    pass  # pragma: no cover


# cache common params to avoid this extra work on every command
# we cant resolve these at module scope because translations break it
_common_params = []


def _get_common_params():
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
    def __init__(self, args, **kwargs):
        super().__init__(**kwargs)
        self.args = args

    def _get_kwargs(self):
        return {"args": self.args, **COMMON_DEFAULTS}


# class _Augment:
#     pass


# def augment(cls):
#     return type('', (_Augment, cls), {})


class Context(TyperContext):
    """
    An extension of the click.Context class that adds a reference to
    the TyperCommand instance so that the Django command can be accessed
    from within click/typer callbacks that take a context.

    e.g. This is necessary so that get_version() behavior can be implemented
    within the Version type itself.
    """

    django_command: "TyperCommand"
    children: t.List["Context"]
    _supplied_params: t.Dict[str, t.Any]

    class ParamDict(dict):
        """
        An extension of dict we use to block updates to parameters that were supplied
        when the command was invoked via call_command. This complexity is introduced
        by the hybrid parsing and option passing inherent to call_command.
        """

        def __init__(self, *args, supplied):
            super().__init__(*args)
            self.supplied = supplied

        def __setitem__(self, key, value):
            if key not in self.supplied:
                super().__setitem__(key, value)

    @property
    def supplied_params(self):
        """
        Get the parameters that were supplied when the command was invoked via
        call_command, only the root context has these.
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
        self.django_command = django_command
        if not django_command and parent:
            self.django_command = parent.django_command

        self.params = self.ParamDict(
            {**self.params, **self.supplied_params},
            supplied=list(self.supplied_params.keys()),
        )
        self.children = []
        if parent:
            parent.children.append(self)


class DjangoAdapterMixin:  # pylint: disable=too-few-public-methods
    context_class: t.Type[click.Context] = Context
    django_command: "TyperCommand"
    callback_is_method: bool = True
    param_converters: t.Dict[str, t.Callable[..., t.Any]] = {}

    def shell_complete(self, ctx: Context, incomplete: str) -> t.List[CompletionItem]:
        """
        By default if the incomplete string is a space and there are no completions
        the click infrastructure will return _files. We'd rather return parameters
        for the command if there are any available.

        TODO - remove parameters that are already provided and do not allow multiple
        specifications.
        """
        completions = super().shell_complete(ctx, incomplete)
        if (
            not completions
            and (incomplete.isspace() or not incomplete)
            and getattr(ctx, "_opt_prefixes", None)
        ):
            completions = super().shell_complete(ctx, min(ctx._opt_prefixes))
        return completions

    def common_params(self):
        return []

    def __init__(
        self,
        *args,
        callback: t.Optional[  # pylint: disable=redefined-outer-name
            t.Callable[..., t.Any]
        ],
        params: t.Optional[t.List[click.Parameter]] = None,
        **kwargs,
    ):
        params = params or []
        self._callback = callback
        expected = [param.name for param in params[1:]]
        self_arg = params[0].name if params else "self"

        def call_with_self(*args, **kwargs):
            ctx = click.get_current_context()
            return callback(
                *args,
                **{
                    # process supplied parameters incase they need type conversion
                    param: self.param_converters.get(param, lambda _, value: value)(
                        ctx, val
                    )
                    if param in ctx.supplied_params
                    else val
                    for param, val in kwargs.items()
                    if param in expected
                },
                **(
                    {self_arg: getattr(ctx, "django_command", None)}
                    if self.callback_is_method
                    else {}
                ),
            )

        super().__init__(  # type: ignore
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
        self.param_converters = {
            param.name: param.process_value for param in self.params
        }


class TyperCommandWrapper(DjangoAdapterMixin, CoreTyperCommand):
    def common_params(self):
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
                not in (self.django_command.suppressed_base_arguments or [])
            ]
        return super().common_params()


class TyperGroupWrapper(DjangoAdapterMixin, CoreTyperGroup):
    def common_params(self):
        if (
            hasattr(self, "django_command") and self.django_command._has_callback
        ) or getattr(self, "common_init", False):
            return [
                param
                for param in _get_common_params()
                if param.name
                not in (self.django_command.suppressed_base_arguments or [])
            ]
        return super().common_params()


class GroupFunction(Typer):
    bound: bool = False
    django_command_cls: t.Type["TyperCommand"]
    _callback: t.Callable[..., t.Any]

    def __get__(self, obj, obj_type=None):
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
        self.django_command_cls = django_command_cls
        # the deepcopy is necessary for instances where classes derive
        # from Command classes and replace/extend commands on groups
        # defined in the base class - this avoids the extending class
        # polluting the base class's command tree
        self.django_command_cls.typer_app.add_typer(deepcopy(self))

    def callback(self, *args, **kwargs):
        raise NotImplementedError(
            _(
                "callback is not supported - the function decorated by group() is the callback."
            )
        )

    def command(
        self,
        name: t.Optional[str] = None,
        *,
        cls: t.Type[TyperCommandWrapper] = TyperCommandWrapper,
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = None,
        help: t.Optional[str] = None,
        epilog: t.Optional[str] = None,
        short_help: t.Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        # Rich settings
        rich_help_panel: t.Union[str, None] = Default(None),
        **kwargs,
    ):
        return super().command(
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
        )

    def group(
        self,
        name: t.Optional[str] = Default(None),
        cls: t.Type[TyperGroupWrapper] = TyperGroupWrapper,
        invoke_without_command: bool = Default(False),
        no_args_is_help: bool = Default(False),
        subcommand_metavar: t.Optional[str] = Default(None),
        chain: bool = Default(False),
        result_callback: t.Optional[t.Callable[..., t.Any]] = Default(None),
        # Command
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = Default(None),
        help: t.Optional[str] = Default(None),
        epilog: t.Optional[str] = Default(None),
        short_help: t.Optional[str] = Default(None),
        options_metavar: str = Default("[OPTIONS]"),
        add_help_option: bool = Default(True),
        hidden: bool = Default(False),
        deprecated: bool = Default(False),
        # Rich settings
        rich_help_panel: t.Union[str, None] = Default(None),
        **kwargs,
    ):
        def create_app(func: CommandFunctionType):
            grp = GroupFunction(
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


def initialize(  # pylint: disable=too-mt.Any-local-variables
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
    help: t.Optional[str] = Default(None),
    epilog: t.Optional[str] = Default(None),
    short_help: t.Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs,
):
    def decorator(func: CommandFunctionType):
        func._typer_callback_ = lambda cmd, **extra: cmd.typer_app.callback(
            name=name or extra.pop("name", None),
            cls=type("_AdaptedCallback", (cls,), {"django_command": cmd}),
            invoke_without_command=invoke_without_command,
            subcommand_metavar=subcommand_metavar,
            chain=chain,
            result_callback=result_callback,
            context_settings=context_settings,
            help=cmd.typer_app.info.help or help,
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
        )(func)
        return func

    return decorator


def command(
    name: t.Optional[str] = None,
    *args,
    cls: t.Type[TyperCommandWrapper] = TyperCommandWrapper,
    context_settings: t.Optional[t.Dict[t.Any, t.Any]] = None,
    help: t.Optional[str] = None,
    epilog: t.Optional[str] = None,
    short_help: t.Optional[str] = None,
    options_metavar: str = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs,
):
    def decorator(func: CommandFunctionType):
        func._typer_command_ = lambda cmd, **extra: cmd.typer_app.command(
            name=name or extra.pop("name", None),
            *args,
            cls=type("_AdaptedCommand", (cls,), {"django_command": cmd}),
            context_settings=context_settings,
            help=help,
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
        )(func)
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
    help: t.Optional[str] = Default(None),
    epilog: t.Optional[str] = Default(None),
    short_help: t.Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    # Rich settings
    rich_help_panel: t.Union[str, None] = Default(None),
    **kwargs,
):
    def create_app(func: CommandFunctionType):
        grp = GroupFunction(
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


class _TyperCommandMeta(type):
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
        help: t.Optional[str] = Default(None),
        epilog: t.Optional[str] = Default(None),
        short_help: t.Optional[str] = Default(None),
        options_metavar: str = Default("[OPTIONS]"),
        add_help_option: bool = Default(True),
        hidden: bool = Default(False),
        deprecated: bool = Default(False),
        rich_markup_mode: MarkupMode = None,
        rich_help_panel: t.Union[str, None] = Default(None),
        pretty_exceptions_enable: bool = Default(True),
        pretty_exceptions_show_locals: bool = Default(True),
        pretty_exceptions_short: bool = Default(True),
    ):
        """
        This method is called when a new class is created.
        """
        try:
            TyperCommand
            is_base_init = False
        except NameError:
            is_base_init = True
        typer_app = None

        if not is_base_init:
            # conform the pretty exception defaults to the settings traceback config
            tb_config = traceback_config()
            if isinstance(pretty_exceptions_enable, DefaultPlaceholder):
                pretty_exceptions_enable = isinstance(tb_config, dict)

            tb_config = tb_config or {}
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
                pretty_exceptions_show_locals=pretty_exceptions_show_locals,
                pretty_exceptions_short=pretty_exceptions_short,
            )

            def handle(self, *args, **options):
                return self.typer_app(
                    args=args,
                    standalone_mode=False,
                    supplied_params=options,
                    django_command=self,
                    complete_var=None,
                    prog_name=f"{sys.argv[0]} {self.typer_app.info.name}",
                )

            attrs = {
                "_handle": attrs.pop("handle", None),
                **attrs,
                "handle": handle,
                "typer_app": typer_app,
            }

        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **kwargs):
        """
        This method is called after a new class is created.
        """
        if cls.typer_app is not None:
            cls.typer_app.info.name = cls.__module__.rsplit(".", maxsplit=1)[-1]
            cls.suppressed_base_arguments = {
                arg.lstrip("--").replace("-", "_")
                for arg in cls.suppressed_base_arguments
            }  # per django docs - allow these to be specified by either the option or param name

            def get_ctor(attr):
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
                        attr.bind(cls)
                        cls._root_groups += 1

                if cmd_cls._handle:
                    ctor = get_ctor(cmd_cls._handle)
                    if ctor:
                        ctor(cls, name=cls.typer_app.info.name)
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


class TyperParser:
    class Action:
        param: click.Parameter
        required: bool = False

        def __init__(self, param: click.Parameter):
            self.param = param

        @property
        def dest(self):
            return self.param.name

        @property
        def nargs(self):
            return 0 if getattr(self.param, "is_flag", False) else self.param.nargs

        @property
        def option_strings(self):
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

        def populate_params(node):
            for param in node.command.params:
                self._actions.append(self.Action(param))
            for child in node.children.values():
                populate_params(child)

        populate_params(self.django_command.command_tree)

    def print_help(self, *command_path: str):
        self.django_command.command_tree.context.info_name = (
            f"{self.prog_name} {self.subcommand}"
        )
        command_node = self.django_command.get_subcommand(*command_path)
        with contextlib.redirect_stdout(self.django_command.stdout):
            command_node.print_help()

    def parse_args(self, args=None, namespace=None):
        try:
            cmd = get_typer_command(self.django_command.typer_app)
            with cmd.make_context(
                info_name=f"{self.prog_name} {self.subcommand}",
                django_command=self.django_command,
                args=list(args or []),
            ) as ctx:
                return _ParsedArgs(args=args or [], **{**COMMON_DEFAULTS, **ctx.params})
        except click.exceptions.Exit:
            sys.exit()

    def add_argument(self, *args, **kwargs):
        raise NotImplementedError(_("add_argument() is not supported"))


class TyperCommand(BaseCommand, metaclass=_TyperCommandMeta):
    """
    A BaseCommand extension class that uses the Typer library to parse
    arguments and options. This class adapts BaseCommand using a light touch
    that relies on most of the original BaseCommand implementation to handle
    default arguments and behaviors.

    The goal of django_typer is to provide full typer style functionality
    while maintaining compatibility with the Django management command system.
    This means that the BaseCommand interface is preserved and the Typer
    interface is added on top of it. This means that this code base is more
    robust to changes in the Django management command system - because most
    of the base class functionality is preserved but mt.Any typer and click
    internals are used directly to achieve this. We rely on robust CI to
    catch breaking changes in the click/typer dependencies.


    TODO - there is a problem with subcommand resolution and make_context()
    that needs to be addressed. Need to understand exactly how click/typer
    does this so it can be broken apart and be interface compatible with
    Django. Also when are callbacks invoked, etc - during make_context? or
    invoke? There is a complexity here with execute().

    TODO - lazy loaded command overrides.
    Should be able to attach to another TyperCommand like this and conflicts would resolve
    based on INSTALLED_APP precedence.

    class Command(TyperCommand, attach='app_label.command_name.subcommand1.subcommand2'):
        ...
    """

    # we do not use verbosity because the base command does not do anything with it
    # if users want to use a verbosity flag like the base django command adds
    # they can use the type from django_typer.types.Verbosity
    suppressed_base_arguments: t.Optional[t.Iterable[str]] = {"verbosity"}

    class CommandNode:
        name: str
        command: t.Union[TyperCommandWrapper, TyperGroupWrapper]
        context: TyperContext
        parent: t.Optional["CommandNode"] = None
        children: t.Dict[str, "CommandNode"]

        def __init__(
            self,
            name: str,
            command: t.Union[TyperCommandWrapper, TyperGroupWrapper],
            context: TyperContext,
            parent: t.Optional["CommandNode"] = None,
        ):
            self.name = name
            self.command = command
            self.context = context
            self.parent = parent
            self.children = {}

        def print_help(self):
            self.command.get_help(self.context)

        def get_command(self, *command_path: str):
            if not command_path:
                return self
            try:
                return self.children[command_path[0]].get_command(*command_path[1:])
            except KeyError:
                raise ValueError(f'No such command "{command_path[0]}"')

    typer_app: t.Optional[Typer] = None
    _num_commands: int = 0
    _has_callback: bool = False
    _root_groups: int = 0

    command_tree: CommandNode

    def __init__(
        self,
        stdout: t.Optional[t.IO[str]] = None,
        stderr: t.Optional[t.IO[str]] = None,
        no_color: bool = False,
        force_color: bool = False,
        **kwargs,
    ):
        super().__init__(
            stdout=stdout,
            stderr=stderr,
            no_color=no_color,
            force_color=force_color,
            **kwargs,
        )
        self.command_tree = self._build_cmd_tree(get_typer_command(self.typer_app))

    def get_subcommand(self, *command_path: str):
        return self.command_tree.get_command(*command_path)

    def _filter_commands(
        self, ctx: TyperContext, cmd_filter: t.Optional[t.List[str]] = None
    ):
        return sorted(
            [
                cmd
                for name, cmd in getattr(
                    ctx.command,
                    "commands",
                    {
                        name: ctx.command.get_command(ctx, name)
                        for name in getattr(ctx.command, "list_commands", lambda _: [])(
                            ctx
                        )
                        or cmd_filter
                        or []
                    },
                ).items()
                if not cmd_filter or name in cmd_filter
            ],
            key=lambda item: item.name,
        )

    def _build_cmd_tree(
        self,
        cmd: CoreTyperCommand,
        parent: t.Optional[Context] = None,
        info_name: t.Optional[str] = None,
        node: t.Optional[CommandNode] = None,
    ):
        ctx = Context(cmd, info_name=info_name, parent=parent, django_command=self)
        current = self.CommandNode(cmd.name, cmd, ctx, parent=node)
        if node:
            node.children[cmd.name] = current
        for cmd in self._filter_commands(ctx):
            self._build_cmd_tree(cmd, parent=ctx, info_name=cmd.name, node=current)
        return current

    def __init_subclass__(cls, **_):
        """Avoid passing typer arguments up the subclass init chain"""
        return super().__init_subclass__()

    def create_parser(self, prog_name: str, subcommand: str, **_):
        return TyperParser(self, prog_name, subcommand)

    def print_help(self, prog_name: str, subcommand: str, *cmd_path: str):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help(*cmd_path)

    def __call__(self, *args, **kwargs):
        """
        Call this command's handle() directly.
        """
        if getattr(self, "_handle", None):
            return self._handle(*args, **kwargs)
        raise NotImplementedError(
            _(
                "{cls} does not implement handle(), you must call the other command "
                "functions directly."
            ).format(cls=self.__class__)
        )
