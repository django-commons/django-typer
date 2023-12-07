r"""
    ___ _                           _____                       
   /   (_) __ _ _ __   __ _  ___   /__   \_   _ _ __   ___ _ __ 
  / /\ / |/ _` | '_ \ / _` |/ _ \    / /\/ | | | '_ \ / _ \ '__|
 / /_//| | (_| | | | | (_| | (_) |  / /  | |_| | |_) |  __/ |   
/___,'_/ |\__,_|_| |_|\__, |\___/   \/    \__, | .__/ \___|_|   
     |__/             |___/               |___/|_|              

"""

import sys
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Type, Union

import click
import typer
from django.core.management.base import BaseCommand
from typer import Typer
from typer.core import TyperCommand as CoreTyperCommand
from typer.core import TyperGroup as CoreTyperGroup
from typer.main import (
    get_command,
    get_params_convertors_ctx_param_name_from_function,
)
from typer.models import CommandFunctionType
from typer.models import Context as TyperContext
from typer.models import Default
from typer.testing import CliRunner

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

VERSION = (0, 1, '0b')

__title__ = 'Django Typer'
__version__ = '.'.join(str(i) for i in VERSION)
__author__ = 'Brian Kohan'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Brian Kohan'


__all__ = [
    'TyperCommand',
    'Context',
    'TyperGroupWrapper',
    'TyperCommandWrapper',
    'callback',
    'command'
]


class _ParsedArgs(SimpleNamespace):  # pylint: disable=too-few-public-methods

    def __init__(self, args, **kwargs):
        super().__init__(**kwargs)
        self.args = args

    def _get_kwargs(self):
        return {
            "args": self.args,
            **_common_options()
        }


class Context(TyperContext):
    """
    An extension of the click.Context class that adds a reference to
    the TyperCommand instance so that the Django command can be accessed
    from within click/typer callbacks that take a context.

    e.g. This is necessary so that get_version() behavior can be implemented
    within the Version type itself.
    """

    django_command: 'TyperCommand'

    def __init__(
        self,
        command: click.Command,  # pylint: disable=redefined-outer-name
        parent: Optional['Context'] = None,
        django_command: Optional['TyperCommand'] = None,
        _resolved_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(command, **kwargs)
        self.django_command = django_command
        if not django_command and parent:
            self.django_command = parent.django_command
        self.params.update(_resolved_params or {})


class DjangoAdapterMixin:  # pylint: disable=too-few-public-methods

    context_class: Type[click.Context] = Context

    def __init__(
        self,
        *args,
        callback: Optional[  # pylint: disable=redefined-outer-name
            Callable[..., Any]
        ] = None,
        params: Optional[List[click.Parameter]] = None,
        **kwargs
    ):
        params = params or []
        self._callback = callback
        expected = [param.name for param in params[1:]]
        self_arg = params[0].name if params else 'self'

        def do_callback(*args, **kwargs):
            if callback:
                return callback(
                    *args,
                    **{
                        param: val for param, val in kwargs.items()
                        if param in expected
                    },
                    **{
                        self_arg: getattr(
                            click.get_current_context(),
                            'django_command',
                            None
                        )
                    }
                )

        super().__init__(  # type: ignore
            *args,
            params=[
                *params[1:],
                *[
                    param for param in COMMON_PARAMS
                    if param.name not in expected
                ]
            ],
            callback=do_callback,
            **kwargs
        )


class TyperCommandWrapper(DjangoAdapterMixin, CoreTyperCommand):
    pass


class TyperGroupWrapper(DjangoAdapterMixin, CoreTyperGroup):
    pass


def callback(
    name: Optional[str] = Default(None),
    *,
    cls: Type[TyperGroupWrapper] = TyperGroupWrapper,
    invoke_without_command: bool = Default(False),
    no_args_is_help: bool = Default(False),
    subcommand_metavar: Optional[str] = Default(None),
    chain: bool = Default(False),
    result_callback: Optional[Callable[..., Any]] = Default(None),
    # Command
    context_settings: Optional[Dict[Any, Any]] = Default(None),
    help: Optional[str] = Default(None),
    epilog: Optional[str] = Default(None),
    short_help: Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    # Rich settings
    rich_help_panel: Union[str, None] = Default(None),
    **kwargs
):

    def decorator(func: CommandFunctionType):
        func._typer_constructor_ = lambda cmd, **extra: cmd.typer_app.callback(
            name=name,
            cls=cls,
            invoke_without_command=invoke_without_command,
            subcommand_metavar=subcommand_metavar,
            chain=chain,
            result_callback=result_callback,
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
            **extra
        )(func)
        return func

    return decorator


def command(
    name: Optional[str] = None,
    *args,
    cls: Type[TyperCommandWrapper] = TyperCommandWrapper,
    context_settings: Optional[Dict[Any, Any]] = None,
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: str = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    # Rich settings
    rich_help_panel: Union[str, None] = Default(None),
    **kwargs
):

    def decorator(func: CommandFunctionType):
        func._typer_constructor_ = lambda cmd, **extra: cmd.typer_app.command(
            name=name,
            *args,
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
            # Rich settings
            rich_help_panel=rich_help_panel,
            **kwargs,
            **extra
        )(func)
        return func

    return decorator


class _TyperCommandMeta(type):

    def __new__(mcs, name, bases, attrs, **kwargs):
        """
        This method is called when a new class is created.
        """
        typer_app = Typer(
            name=mcs.__module__.rsplit('.', maxsplit=1)[-1],
            cls=TyperGroupWrapper,
            help=attrs.get('help', typer.models.Default(None)),
            **kwargs
        )

        def handle(self, *args, **options):
            return self.typer_app(
                args=args,
                standalone_mode=False,
                _resolved_params=options,
                django_command=self
            )

        return super().__new__(
            mcs,
            name,
            bases,
            {
                '_handle': attrs.pop('handle', None),
                **attrs,
                'handle': handle,
                'typer_app': typer_app
            }
        )

    def __init__(cls, name, bases, attrs, **kwargs):
        """
        This method is called after a new class is created.
        """
        cls.typer_app.info.name = cls.__module__.rsplit('.', maxsplit=1)[-1]
        if cls._handle:
            if hasattr(cls._handle, '_typer_constructor_'):
                cls._handle._typer_constructor_(
                    cls,
                    name=cls.typer_app.info.name
                )
                del cls._handle._typer_constructor_
            else:
                cls.typer_app.command(
                    cls.typer_app.info.name,
                    cls=TyperCommandWrapper
                )(cls._handle)

        for attr in attrs.values():
            if hasattr(attr, '_typer_constructor_'):
                attr._typer_constructor_(cls)
                del attr._typer_constructor_

        super().__init__(name, bases, attrs, **kwargs)


class _TyperParserAdapter:

    _actions: List[Any] = []
    _mutually_exclusive_groups: List[Any] = []

    django_command: 'TyperCommand'
    prog_name: str
    subcommand: str

    def __init__(
        self,
        django_command: 'TyperCommand',
        prog_name,
        subcommand
    ):
        self.django_command = django_command
        self.prog_name = prog_name
        self.subcommand = subcommand

    def print_help(self):
        typer.echo(
            CliRunner().invoke(
                self.django_command.typer_app,
                ['--help']
            ).output
        )

    def parse_args(self, args = None, namespace=None):
        try:
            cmd = get_command(self.django_command.typer_app)
            with cmd.make_context(
                f'{self.prog_name} {self.subcommand}',
                list(args or []),
                django_command=self.django_command
            ) as ctx:
                if ctx.protected_args:
                    p_args = [*ctx.protected_args, *ctx.args]
                    if not cmd.chain:  # type: ignore
                        (
                            cmd_name,
                            cmd,
                            c_args
                        ) = cmd.resolve_command(  # type: ignore
                            ctx,
                            p_args
                        )
                        assert cmd is not None
                        sub_ctx = cmd.make_context(
                            cmd_name,
                            c_args,
                            parent=ctx,
                            django_command=self.django_command
                        )
                        return _ParsedArgs(
                            args=p_args,
                            **{
                                **_common_options(),
                                **ctx.params,
                                **sub_ctx.params
                            }
                        )
                    else:
                        pass
                else:
                    return _ParsedArgs(
                        args=args or [],
                        **{
                            **_common_options(),
                            **ctx.params
                        }
                    )

        except click.exceptions.Exit:
            sys.exit()

    def add_argument(self, *args, **kwargs):
        pass


def _common_options(
    version: Version = False,
    verbosity: Verbosity = 1,
    settings: Settings = '',
    pythonpath: PythonPath = None,
    traceback: Traceback = False,
    no_color: NoColor = False,
    force_color: ForceColor = False,
    skip_checks: SkipChecks = False
):
    return {
        'version': version,
        'verbosity': verbosity,
        'settings': settings,
        'pythonpath': pythonpath,
        'traceback': traceback,
        'no_color': no_color,
        'force_color': force_color,
        'skip_checks': skip_checks
    }


COMMON_PARAMS = get_params_convertors_ctx_param_name_from_function(
    _common_options
)[0]
COMMON_PARAM_NAMES = [param.name for param in COMMON_PARAMS]


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
    of the base class functionality is preserved but many typer and click 
    internals are used directly to achieve this. We rely on robust CI to 
    catch breaking changes in the click/typer dependencies.


    TODO - there is a problem with subcommand resolution and make_context()
    that needs to be addressed. Need to understand exactly how click/typer 
    does this so it can be broken apart and be interface compatible with 
    Django. Also when are callbacks invoked, etc - during make_context? or 
    invoke? There is a complexity here with execute().
    """

    typer_app: Typer

    @property
    def stealth_options(self):
        """
        This is the only way to inject the set of valid parameters into 
        call_command because it does its own parameter validation - otherwise
        TypeErrors are thrown.
        """
        return tuple(COMMON_PARAM_NAMES)

    def __init_subclass__(cls, **_):
        """Avoid passing typer arguments up the subclass init chain"""
        return super().__init_subclass__()

    def create_parser(self, prog_name, subcommand, **_):
        return _TyperParserAdapter(self, prog_name, subcommand)

    def handle(self, *args: Any, **options: Any) -> str | None:
        ...

    def __call__(self, *args, **kwargs):
        """
        Call this command's handle() directly.
        """
        if hasattr(self, '_handle'):
            return self._handle(*args, **kwargs)
        raise NotImplementedError(f'{self.__class__}')
