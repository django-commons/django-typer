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
from dataclasses import dataclass
from importlib import import_module
from types import MethodType, SimpleNamespace
from copy import deepcopy

import click
from django.conf import settings
from django.core.management import get_commands
from django.core.management.base import BaseCommand
from typer import Typer
from typer.core import TyperCommand as CoreTyperCommand
from typer.core import TyperGroup as CoreTyperGroup
from typer.main import MarkupMode
from typer.main import get_command as get_typer_command
from typer.main import get_params_convertors_ctx_param_name_from_function
from typer.models import CommandFunctionType
from typer.models import Context as TyperContext
from typer.models import Default

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

VERSION = (0, 3, "0b")

__title__ = "Django Typer"
__version__ = ".".join(str(i) for i in VERSION)
__author__ = "Brian Kohan"
__license__ = "MIT"
__copyright__ = "Copyright 2023 Brian Kohan"


__all__ = [
    "TyperCommand",
    "Context",
    "TyperGroupWrapper",
    "TyperCommandWrapper",
    "callback",
    "command",
    "get_command",
]

"""
TODO
- add translation support in helps
- documentation
- linting
- type hints
"""

try:
    from rich.traceback import install

    traceback_config = getattr(settings, "RICH_TRACEBACK_CONFIG", {"show_locals": True})
    if isinstance(traceback_config, dict):
        install(**traceback_config)
except ImportError:
    pass


def get_command(
    command_name: str,
    *subcommand: str,
    stdout: t.Optional[t.IO[str]] = None,
    stderr: t.Optional[t.IO[str]] = None,
    no_color: bool = False,
    force_color: bool = False,
):
    # todo - add a __call__ method to the command class if it is not a TyperCommand and has no
    # __call__ method - this will allow this interface to be used for standard commands
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
    pass


COMMON_PARAMS = get_params_convertors_ctx_param_name_from_function(_common_options)[0]
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

    def __init__(
        self,
        command: click.Command,  # pylint: disable=redefined-outer-name
        parent: t.Optional["Context"] = None,
        django_command: t.Optional["TyperCommand"] = None,
        supplied_params: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs,
    ):
        super().__init__(command, parent=parent, **kwargs)
        supplied_params = supplied_params or {}
        self.django_command = django_command
        if not django_command and parent:
            self.django_command = parent.django_command
        self.params = self.ParamDict(
            {**self.params, **supplied_params},
            supplied=list(supplied_params.keys()),
        )
        self.children = []
        if parent:
            parent.children.append(self)


class DjangoAdapterMixin:  # pylint: disable=too-few-public-methods
    context_class: t.Type[click.Context] = Context
    django_command: "TyperCommand"
    callback_is_method: bool = True

    def common_params(self):
        return []

    def __init__(
        self,
        *args,
        callback: t.Optional[  # pylint: disable=redefined-outer-name
            t.Callable[..., t.Any]
        ] = None,
        params: t.Optional[t.List[click.Parameter]] = None,
        **kwargs,
    ):
        params = params or []
        self._callback = callback
        expected = [param.name for param in params[1:]]
        self_arg = params[0].name if params else "self"

        def call_with_self(*args, **kwargs):
            if callback:
                return callback(
                    *args,
                    **{
                        param: val for param, val in kwargs.items() if param in expected
                    },
                    **(
                        {
                            self_arg: getattr(
                                click.get_current_context(), "django_command", None
                            )
                        }
                        if self.callback_is_method
                        else {}
                    ),
                )
            return None

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
                for param in COMMON_PARAMS
                if param.name in (self.django_command.django_params or [])
            ]
        return []


class TyperGroupWrapper(DjangoAdapterMixin, CoreTyperGroup):
    def common_params(self):
        if hasattr(self, "django_command") and self.django_command._has_callback:
            return [
                param
                for param in COMMON_PARAMS
                if param.name in (self.django_command.django_params or [])
            ]
        return []


class TyperWrapper(Typer):
    bound: bool = False
    django_command_cls: t.Type["TyperCommand"]

    def __init__(self, *args, **kwargs):
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
            "callback is not supported - the function decorated by group() is the callback."
        )

    def command(
        self, *args, cls: t.Type[TyperCommandWrapper] = TyperCommandWrapper, **kwargs
    ):
        return super().command(*args, cls=cls, **kwargs)

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
            app = TyperWrapper(
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
            self.add_typer(app)
            app.bound = True
            return app

        return create_app


def callback(  # pylint: disable=too-mt.Any-local-variables
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
        return TyperWrapper(
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
        add_completion: bool = True,
        rich_markup_mode: MarkupMode = None,
        rich_help_panel: t.Union[str, None] = Default(None),
        pretty_exceptions_enable: bool = True,
        pretty_exceptions_show_locals: bool = True,
        pretty_exceptions_short: bool = True,
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
                add_completion=add_completion,
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

            def get_ctor(attr):
                return getattr(
                    attr, "_typer_command_", getattr(attr, "_typer_callback_", None)
                )

            # because we're mapping a non-class based interface onto a class based interface, we have to
            # handle this class mro stuff manually here
            for cmd_cls, cls_attrs in [
                *[(base, vars(base)) for base in reversed(bases)],
                (cls, attrs),
            ]:
                if not issubclass(cmd_cls, TyperCommand) or cmd_cls is TyperCommand:
                    continue
                for attr in [*cls_attrs.values(), cls._handle]:
                    cls._num_commands += hasattr(attr, "_typer_command_")
                    cls._has_callback |= hasattr(attr, "_typer_callback_")
                    if isinstance(attr, TyperWrapper) and not attr.bound:
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
                        {"django_command": cls, "callback_is_method": False},
                    )
                )(_common_options)

        super().__init__(name, bases, attrs, **kwargs)


class TyperParser:
    @dataclass(frozen=True)
    class Action:
        dest: str
        required: bool = False

        @property
        def option_strings(self):
            return [self.dest]

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
                self._actions.append(self.Action(param.name))
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
                params = ctx.params

                def discover_parsed_args(ctx):
                    # todo is this necessary?
                    for child in ctx.children:
                        discover_parsed_args(child)
                        params.update(child.params)

                discover_parsed_args(ctx)

                return _ParsedArgs(args=args or [], **{**COMMON_DEFAULTS, **params})
        except click.exceptions.Exit:
            sys.exit()

    def add_argument(self, *args, **kwargs):
        pass


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
    django_params: t.Optional[
        t.List[
            t.Literal[
                "version",
                "settings",
                "pythonpath",
                "traceback",
                "no_color",
                "force_color",
                "skip_checks",
            ]
        ]
    ] = [param.name for param in COMMON_PARAMS if param.name != "verbosity"]

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
        if hasattr(self, "_handle"):
            return self._handle(*args, **kwargs)
        raise NotImplementedError(f"{self.__class__}")
