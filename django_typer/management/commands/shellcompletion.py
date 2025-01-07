"""
The shellcompletion command is a Django_ management command that installs and removes
shellcompletion scripts for supported shells (bash, fish, zsh, powershell). This
command is also the entry point for running the completion logic and can be used to
debug completer code.

.. typer:: django_typer.management.commands.shellcompletion.Command:typer_app
    :prog: manage.py shellcompletion
    :width: 80
    :convert-png: latex

:func:`~django_typer.management.commands.shellcompletion.Command.install` invokes typer's shell
completion installation logic, but does have to patch the installed scripts. This is because
there is only one installation for all Django_ management commands, not each individual command.
The completion logic here will failover to Django_'s builtin autocomplete if the command in
question is not a :class:`~django_typer.TyperCommand`. To promote compatibility with other
management command libraries or custom completion logic, a fallback completion function can also
be specified.
"""

import collections.abc as cabc
import contextlib
import io
import os
import platform
import re
import sys
import typing as t
from abc import abstractmethod
from importlib.resources import files
from pathlib import Path
from types import ModuleType

from click.core import Command as ClickCommand
from click.parser import split_arg_string
from click.shell_completion import CompletionItem, ShellComplete, add_completion_class
from django.core.management import CommandError, ManagementUtility
from django.template import Context, Engine
from django.template.backends.django import Template as DjangoTemplate
from django.template.base import Template as BaseTemplate
from django.template.loader import TemplateDoesNotExist, get_template
from django.utils.module_loading import import_string
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from shellingham import ShellDetectionFailure, detect_shell
from typer import Argument, Option
from typer.main import get_command as get_typer_command

from django_typer.completers import these_strings
from django_typer.management import TyperCommand, command, get_command, initialize
from django_typer.types import COMMON_PANEL
from django_typer.utils import get_usage_script, get_win_shell

DETECTED_SHELL = None

try:
    DETECTED_SHELL = detect_shell()[0]
except (ShellDetectionFailure, RuntimeError):
    pass


class DjangoTyperShellCompleter(ShellComplete):
    """
    An extension to the click shell completion classes that provides a Django specific
    shell completion implementation. If you wish to support a new shell, you must
    derive from this class, implement all of the abstract methods, and register the
    class with
    :func:`~django_typer.management.commands.shellcompletion.register_completion_class`

    :param cli: The click command object to complete
    :param ctx_args: Additional context arguments to pass to the typer/click context of the
        management command being completed
    :param prog_name: The name of the command to complete
    :param complete_var: The name of the environment variable to pass the completion string
        (unused)
    :param command: The Django shellcompletion command
    :param command_str: The command string to complete
    :param command_args: The command arguments to complete
    :param template: The name of the shell completion script template
    :param color: Allow or disallow color and formatting in the completion output
    """

    template: str
    """
    The name of the shell completion function script template.
    """

    color: bool = False
    """
    By default, allow or disallow color and formatting in the completion output.
    """

    supports_scripts: bool = False
    """
    Does the shell support completions for uninstalled scripts? (i.e. not on the path)
    """

    complete_var: str = ""

    command: "Command"
    command_str: str
    command_args: t.List[str]

    console = None  # type: ignore[var-annotated]
    console_buffer: io.StringIO

    def __init__(
        self,
        cli: t.Optional[ClickCommand] = None,
        ctx_args: cabc.MutableMapping[str, t.Any] = {},
        prog_name: str = "",
        complete_var: str = "",
        command: t.Optional["Command"] = None,
        command_str: t.Optional[str] = None,
        command_args: t.Optional[t.List[str]] = None,
        template: t.Optional[str] = None,
        color: t.Optional[bool] = None,
        **kwargs,
    ):
        # we don't always need the initialization parameters during completion
        self.prog_name = prog_name
        if command:
            self.command = command
        if command_str is not None:
            self.command_str = command_str
        if command_args is not None:
            self.command_args = command_args
        if template is not None:
            self.template = template
        if color is not None:
            self.color = color

        self.console_buffer = io.StringIO()
        try:
            from rich.console import Console

            self.console = Console(
                color_system="auto" if self.color else None,
                force_terminal=True,
                file=self.console_buffer,
            )
        except ImportError:
            pass

        if cli:
            super().__init__(
                cli=cli,
                ctx_args=ctx_args,
                complete_var=complete_var,
                prog_name=prog_name,
                **kwargs,
            )

    @property
    def source_template(self) -> str:  # type: ignore
        """
        The contents of the shell's completion script template.
        """
        return Path(self.load_template().origin.name).read_text()

    def get_completions(
        self, args: t.List[str], incomplete: str
    ) -> t.List[CompletionItem]:
        """
        need to remove the django command name from the arg completions
        """
        if self.command.fallback:
            return self.command.fallback(args, incomplete)
        return super().get_completions(args[1:], incomplete)

    def get_completion_args(self) -> t.Tuple[t.List[str], str]:
        """
        Return the list of completion arguments and the incomplete string.
        """
        cwords = self.command_args
        if self.command_str and self.command_str[-1].isspace():
            # if the command string ends with a space, the incomplete string is empty
            cwords.append("")
        return (
            cwords[:-1],
            cwords[-1] if cwords else "",
        )

    def source_vars(self) -> t.Dict[str, t.Any]:
        """
        This returns the context that will be used to render the completion script template.

        From the base class we inherit the following variables:

        * **complete_func**: the name to use for the shell's completion function
        * **complete_var**: unused because we do not use environment variables
            to pass the completion string
        * **prog_name**: the name of the command to complete

        We add the following variables:

        * **manage_script**: the manage script object - will be either a string or a Path, if it
          is a Path it will be absolute and this indicates that the script is not installed on the
          path
        * **manage_script_name**: the name of the Django manage script
        * **python**: the path to the python interpreter that is running the shellcompletion
          command
        * **django_command**: the name of the Django shellcompletion command - you may change this
          to something other than 'shellcompletion' to provide custom complete logic
        * **color**: the color flag to pass to shellcompletion i.e. --(force|no)-color
        * **fallback**: the fallback option to pass to ``shellcompletion complete``
        * **is_installed**: whether or not the manage script is a command on the path
        * **shell**: the name of the shell
        """
        return {
            **super().source_vars(),
            "manage_script": self.command.manage_script,
            "manage_script_name": self.command.manage_script_name,
            "python": sys.executable,
            "django_command": self.command.__module__.split(".")[-1],
            "color": "--force-color"
            if self.color
            else "--no-color"
            if self.command.force_color
            else "",
            "fallback": f" --fallback {self.command.fallback_import}"
            if self.command.fallback
            else "",
            "is_installed": not isinstance(self.command.manage_script, Path),
            "shell": self.name,
        }

    def load_template(self) -> t.Union[BaseTemplate, DjangoTemplate]:
        """
        Return a compiled Template object for the completion script template.
        """
        try:
            return get_template(self.template)  # type: ignore
        except TemplateDoesNotExist:
            # handle case where templating is not configured to find our default
            # templates
            return Engine(
                dirs=[str(files("django_typer").joinpath("templates"))],
                libraries={
                    "default": "django.template.defaulttags",
                    "filter": "django.template.defaultfilters",
                },
            ).get_template(self.template)

    def source(self) -> str:
        """
        Render the completion script template to a string.
        """
        try:
            return self.load_template().render(self.source_vars())  # type: ignore
        except TypeError:
            # it is annoying that get_template() and DjangoEngine.get_template() return different
            # interfaces
            return self.load_template().render(Context(self.source_vars()))  # type: ignore

    @abstractmethod
    def install(self) -> Path:
        """
        Deriving classes must implement this method to install the completion script.

        This method should return the path to the installed script.
        """
        ...

    @abstractmethod
    def uninstall(self):
        """
        Deriving classes must implement this method to uninstall the completion script.
        """
        ...

    def process_rich_text(self, text: str) -> str:
        """
        Removes rich text markup from a string if color is disabled, otherwise it
        will render the rich markup to ansi control codes. If rich is not installed,
        none of this happens and the markup will be passed through as is.
        """
        if self.console:
            if self.color:
                self.console_buffer.truncate(0)
                self.console_buffer.seek(0)
                self.console.print(text, end="")
                return self.console_buffer.getvalue()
            else:
                return "".join(
                    segment.text for segment in self.console.render(text)
                ).rstrip("\n")
        return text


_completers: t.Dict[str, t.Type[DjangoTyperShellCompleter]] = {}


def register_completion_class(cls: t.Type[DjangoTyperShellCompleter]) -> None:
    """
    Register a shell completion class for use with the Django shellcompletion command.
    """
    _completers[cls.name] = cls
    add_completion_class(cls)


def django_autocomplete(args: t.List[str], incomplete: str) -> t.List[CompletionItem]:
    # spoof bash environment variables
    # the first one is lopped off, so we insert a placeholder 0
    args = ["0", *args]
    if args[-1] != incomplete:
        args.append(incomplete)
    else:  # pragma: no cover
        pass
    os.environ["COMP_WORDS"] = " ".join(args)
    os.environ["COMP_CWORD"] = str(args.index(incomplete))
    os.environ["DJANGO_AUTO_COMPLETE"] = "1"
    dj_manager = ManagementUtility(args)
    capture_completions = io.StringIO()
    with contextlib.redirect_stdout(capture_completions):
        try:
            dj_manager.autocomplete()
        except SystemExit:
            pass
    return [
        CompletionItem(item) for item in capture_completions.getvalue().split() if item
    ]


class Command(TyperCommand):
    """
    This command installs autocompletion for the current shell. This command uses the typer/click
    autocompletion scripts to generate the autocompletion items, but monkey patches the scripts
    to invoke our bundled shell complete script which fails over to the django autocomplete
    function when the command being completed is not a :class:`~django_typer.TyperCommand`. When
    the django autocomplete function is used we also wrap it so that it works for any supported
    click/typer shell, not just bash.

    We also provide a remove command to easily remove the installed script.

    Great pains are taken to use the upstream dependency's shell completion logic. This is so
    advances and additional shell support implemented upstream should just work. However, it
    would be possible to add support for new shells here using the pluggable logic that click
    provides. It is probably a better idea however to add support for new shells at the typer
    level.

    Shell autocompletion can be brittle with every shell having its own quirks and nuances. We
    make a good faith effort here to support all the shells that typer/click support, but there
    can easily be system specific configuration issues that prevent this from working. In those
    cases users should refer to the online documentation for their specific shell to troubleshoot.
    """

    help = t.cast(str, _("Install autocompletion for the current shell."))

    # disable the system checks - no reason to run these for this one-off command
    requires_system_checks = []
    requires_migrations_checks = False

    # remove unnecessary django command base parameters - these just clutter the help
    suppressed_base_arguments = {
        "version",
        "skip_checks",
        "verbosity",
    }

    _shell: t.Optional[str] = DETECTED_SHELL
    shell_module: ModuleType

    ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    _fallback: t.Optional[t.Callable[[t.List[str], str], t.List[CompletionItem]]] = None
    _manage_script: t.Optional[t.Union[str, Path]] = None

    @property
    def fallback(
        self,
    ) -> t.Optional[t.Callable[[t.List[str], str], t.List[CompletionItem]]]:
        return self._fallback

    @fallback.setter
    def fallback(self, fb: t.Optional[str]):
        try:
            self._fallback = import_string(fb) if fb else django_autocomplete
        except ImportError as err:
            raise CommandError(
                gettext("Unable to import fallback completion function: {err}").format(
                    err=str(err)
                )
            ) from err

    @property
    def fallback_import(self) -> t.Optional[str]:
        return (
            f"{self.fallback.__module__}.{self.fallback.__name__}"
            if self.fallback
            else None
        )

    @property
    def manage_script(self) -> t.Union[str, Path]:
        """
        Returns the name of the manage command as a string if it is available as a command
        on the user path. If it is a script that is not available as a command on the path
        it will return an absolute Path object to the script.
        """
        # We do not want to hardcode this as 'manage.py' because users are free to rename and
        # implement their own manage scripts! The safest way to do this is therefore to fetch
        # the name of the script that invoked the shellcompletion command and determine if that
        # script is available on the user's path or not.

        # Most shell's completion infrastructure works best if the commands are available on the
        # path. However, it is common for Django development to be done in a virtual environment
        # with a manage.py script being invoked directly as a script. Completion should work in
        # this case as well, but it does complicate the installation for some shell's so we must
        # first figure out which mode we are in.
        if not self._manage_script:
            self.manage_script = None  # type: ignore
        return self._manage_script  # type: ignore

    @manage_script.setter
    def manage_script(self, script: t.Optional[str]):
        self._manage_script = get_usage_script(script)
        if isinstance(self._manage_script, Path):
            self._manage_script = self._manage_script.absolute()

    @property
    def manage_script_name(self) -> str:
        """
        Get the name of the manage script as a command available from the shell's path.
        """
        if isinstance(self.manage_script, Path):
            return self.manage_script.name
        return self.manage_script

    @property
    def shell(self) -> str:
        """
        Get the active shell. If not explicitly set, it first tries to find the shell
        in the environment variable shell complete scripts set and failing that it will try
        to autodetect the shell.
        """
        assert self._shell
        return self._shell

    @shell.setter
    def shell(self, shell: t.Optional[str]):
        """Set the shell to install autocompletion for."""
        if shell:
            self._shell = shell
        if self._shell is None:
            raise CommandError(
                gettext(
                    "Please specify the shell to install or remove "
                    "autocompletion for. Unable to detect shell."
                )
            )
        elif self._shell == "cmd" and platform.system() == "Windows":
            try:
                self._shell = get_win_shell()
            except ShellDetectionFailure:
                pass

    @property
    def shell_class(self):
        global _completers
        try:
            return _completers[self.shell]
        except KeyError as err:
            raise CommandError(
                gettext("Unsupported shell: {shell}").format(shell=self.shell)
            ) from err

    @initialize()
    def init(
        self,
        shell: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _("The shell to use."),
                ),
                metavar="SHELL",
                shell_complete=these_strings(_completers.keys()),
            ),
        ] = DETECTED_SHELL,
        no_color: t.Annotated[
            t.Optional[bool],
            Option(
                "--no-color",
                help=t.cast(
                    str,
                    _(
                        "Filter terminal formatting control sequences out of completion text."
                    ),
                ),
                rich_help_panel=COMMON_PANEL,
            ),
        ] = None,
        force_color: t.Annotated[
            bool,
            Option(
                "--force-color",
                help=t.cast(
                    str,
                    _(
                        "Allow terminal formatting control sequences in completion text."
                    ),
                ),
                rich_help_panel=COMMON_PANEL,
            ),
        ] = False,
    ) -> "Command":
        self.shell = shell  # type: ignore[assignment]
        assert self.shell
        self.force_color = force_color
        self.no_color = (not self.shell_class.color) if no_color is None else no_color
        if self.force_color:
            self.no_color = False
        return self

    @command(
        help=t.cast(str, _("Install autocompletion for the current or given shell."))
    )
    def install(
        self,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The name of the django manage script to install autocompletion for if "
                        "different than the script used to invoke this command."
                    ),
                )
            ),
        ] = None,
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The python import path to a fallback complete function to use when "
                        "the completion command is not a TyperCommand."
                    ),
                )
            ),
        ] = None,
        template: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The name of the template to use for the shell completion script."
                    ),
                )
                # todo - add template name completer - see django-render-static
            ),
        ] = None,
    ):
        """
        Install autocompletion for the given shell. If the shell is not specified, it will
        try to detect the shell. If the shell is not detected, it will fail.

        We run the upstream typer installation routines, with some augmentation.

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:install
            :width: 85
            :convert-png: latex
        """
        self.fallback = fallback  # type: ignore[assignment]
        self.manage_script = manage_script  # type: ignore[assignment]
        if isinstance(self.manage_script, Path):
            if not self.shell_class.supports_scripts:
                raise CommandError(
                    gettext(
                        "Shell {shell} does not support autocompletion for scripts that are not "
                        "installed on the path. You must create an entry point for {script_name}. "
                        "See {link}."
                    ).format(
                        shell=self.shell,
                        script_name=self.manage_script_name,
                        link="https://setuptools.pypa.io/en/latest/userguide/entry_point.html",
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        gettext(
                            "It is not recommended to install tab completion for a script not on "
                            "the path because completions will likely only work if the script is "
                            "invoked from the same location and using the same relative path. You "
                            "may wish to create an entry point for {script_name}. See {link}."
                        ).format(
                            script_name=self.manage_script_name,
                            link="https://setuptools.pypa.io/en/latest/userguide/entry_point.html",
                        ),
                    )
                )

        install_path = self.shell_class(
            prog_name=str(manage_script or self.manage_script_name),
            command=self,
            template=template,
            color=not self.no_color or self.force_color,
        ).install()
        self.stdout.write(
            self.style.SUCCESS(
                gettext("Installed autocompletion for {shell} @ {install_path}").format(
                    shell=self.shell, install_path=install_path
                )
            )
        )

    @command(
        help=t.cast(str, _("Uninstall autocompletion for the current or given shell."))
    )
    def uninstall(
        self,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The name of the django manage script to remove shell completion for if "
                        "different than the script used to invoke this command."
                    ),
                )
            ),
        ] = None,
    ):
        """
        Remove the autocompletion for the given shell. If the shell is not specified, it will
        try to detect the shell. If the shell is not detected, it will fail.

        Since the installation routine is upstream we first run install to determine where the
        completion script is installed and then we remove it.

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:remove
            :prog: shellcompletion
            :width: 80
            :convert-png: latex

        """
        self.manage_script = manage_script  # type: ignore[assignment]
        self.shell_class(
            prog_name=str(manage_script or self.manage_script_name),
            command=self,
            color=not self.no_color or self.force_color,
        ).uninstall()
        self.stdout.write(
            self.style.WARNING(
                gettext("Uninstalled autocompletion for {shell}.").format(
                    shell=self.shell
                )
            )
        )

    @command(
        help=t.cast(str, _("Generate autocompletion for command string.")), hidden=False
    )
    def complete(
        self,
        command: t.Annotated[
            str,
            Argument(
                help=t.cast(
                    str, _("The command string to generate completion suggestions for.")
                ),
            ),
        ] = "",
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The python import path to a fallback complete function to use when "
                        "the completion command is not a TyperCommand. By default, the builtin "
                        "django autocomplete function is used."
                    ),
                )
            ),
        ] = None,
    ):
        """
        We implement the shell complete generation script as a Django command because the
        Django environment needs to be bootstrapped for it to work. This also allows
        us to test completion logic in a platform agnostic way.

        .. tip::

            This command is super useful for debugging shell_complete logic. For example to
            enter into the debugger, we could set a breakpoint in our ``shell_complete`` function
            for the option parameter and then run the following command:

            .. code-block:: bash

                $ ./manage.py shellcompletion complete "./manage.py your_command --option "

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:complete
            :prog: shellcompletion
            :width: 80
            :convert-png: latex
        """
        args = split_arg_string(command)
        if args:
            try:
                # lop the manage script off the front if it's there
                if args[0] == self.manage_script_name:
                    args = args[1:]
                elif Path(args[0]).resolve() == Path(sys.argv[0]).resolve():
                    args = args[1:]
            except (TypeError, ValueError, OSError):  # pragma: no cover
                pass

        def get_completion() -> str:
            if args:
                # we first need to figure out which command is being invoked
                # but we cant be sure which index the command name is at so
                # we try to fetch each in order and assume the first arg
                # that resolves to a command is the command
                cmd = None
                cmd_idx = -1
                try:
                    while cmd is None:
                        cmd_idx += 1
                        try:
                            cmd = get_command(args[cmd_idx])
                        except KeyError:
                            pass
                except IndexError:
                    if command.endswith(" "):
                        # unrecognized command
                        return ""
                    # fall through to fallback

                if isinstance(cmd, TyperCommand):
                    # this will exit out so no return is needed here
                    return self.shell_class(
                        cli=get_typer_command(cmd.typer_app),
                        ctx_args={"django_command": cmd},
                        prog_name="",
                        complete_var="",
                        command=self,
                        command_str=command,
                        command_args=args,
                        color=not self.no_color or self.force_color,
                    ).complete()

            # only try to set the fallback if we have to use it
            self.fallback = fallback  # type: ignore[assignment]
            return self.shell_class(
                command=self,
                command_str=command,
                command_args=args,
                color=not self.no_color or self.force_color,
            ).complete()

        def strip_color(text: str) -> str:
            """
            Strip ANSI color codes from a string.
            """
            if self.no_color:
                return self.ANSI_ESCAPE_RE.sub("", text)
            return text

        return strip_color(get_completion())


from .shells.bash import BashComplete  # noqa: E402
from .shells.fish import FishComplete  # noqa: E402
from .shells.powershell import PowerShellComplete, PwshComplete  # noqa: E402
from .shells.zsh import ZshComplete  # noqa: E402

register_completion_class(ZshComplete)
register_completion_class(BashComplete)
register_completion_class(PowerShellComplete)
register_completion_class(PwshComplete)
register_completion_class(FishComplete)
