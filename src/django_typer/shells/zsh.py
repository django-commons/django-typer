import os
import typing as t
from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from . import DjangoTyperShellCompleter


class ZshComplete(DjangoTyperShellCompleter):
    """
    This completer class supports Zsh_. Completion scripts are installed to the
    ``.zfunc`` directory in the user's home directory. Style and completion
    initialization instructions are added to the user's ``.zshrc`` file if needed.

    Returned suggestions are delimited by newlines. Each suggestion is on three lines:

    * The first line is the type of the completion.
    * The second line is the value of the completion.
    * The third line is the help text for the completion.

    See also:
    https://github.com/zsh-users/zsh-completions/blob/master/zsh-completions-howto.org
    """

    name = "zsh"
    """
    shell executable.
    """

    template = "shell_complete/zsh.sh"
    """
    The template used to render the zsh completion script.
    """

    supports_scripts = True
    """
    The zsh completer supports script invocations.
    """

    color = False
    """
    Zsh_ does support ansi control codes in completion suggestions, but we disable them
    by default.
    """

    def get_user_profile(self) -> Path:
        """
        Get the user's .zshrc file. It is located in the user's home directory by
        default unless the ``ZDOTDIR`` environment variable is set.
        """
        return Path(os.environ.get("ZDOTDIR", Path.home())) / ".zshrc"

    @cached_property
    def install_dir(self) -> Path:
        """
        The directory where completer scripts will be installed.
        """
        install_dir = self.get_user_profile().parent / ".zfunc"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def format_completion(self, item: CompletionItem) -> str:
        hlp = self.process_rich_text(item.help.replace("\n", " ")) if item.help else "_"
        return f"{item.type}\n{self.process_rich_text(item.value)}\n{hlp}"

    def install(self, prompt: bool = True) -> t.List[Path]:
        assert self.prog_name
        zshrc = self.get_user_profile()
        zshrc_source = ""
        start_line = 0
        if zshrc.is_file():
            zshrc_source = zshrc.read_text()
            start_line = zshrc_source.count("\n") + 2
        additions = ""
        if "fpath" not in zshrc_source:
            additions += f"if type brew &>/dev/null; then{os.linesep}"
            additions += (
                f"\tfpath=(~/.zfunc $(brew --prefix)/share/zsh-completions $fpath)"
                f"{os.linesep}"
            )
            additions += f"else{os.linesep}"
            additions += f"\tfpath=(~/.zfunc $fpath){os.linesep}"
            additions += f"fi{os.linesep}{os.linesep}"
        if "compinit" not in zshrc_source:
            additions += f"autoload -Uz compinit{os.linesep}"
            additions += f"compinit{os.linesep}"

        style = (
            f"zstyle ':completion:*:*:{self.prog_name}:*' menu select"
            if self.is_installed
            else "zstyle ':completion:*' menu select"
        )
        if style not in zshrc_source:
            additions += f"{style}{os.linesep}"

        edited = []
        script = self.install_dir / f"_{self.prog_name}"
        if additions:
            if self.prompt(
                prompt=prompt,
                source=additions,
                file=zshrc,
                start_line=start_line,
            ):
                Path.home().mkdir(parents=True, exist_ok=True)
                with open(zshrc, "a") as zrc_file:
                    zrc_file.write(f"{os.linesep}{additions}")
                edited.append(zshrc)
        source = self.source()
        if self.prompt(prompt=prompt, source=source, file=script, start_line=0):
            script.write_text(self.source())
            edited.append(script)
        return edited

    def uninstall(self):
        script = self.install_dir / f"_{self.prog_name}"
        if script.is_file():
            script.unlink()

        zshrc = self.get_user_profile()
        if zshrc.is_file():
            zshrc_source = zshrc.read_text()
            zshrc.write_text(
                zshrc_source.replace(
                    f"zstyle ':completion:*:*:{self.prog_name}:*' menu select\n", ""
                )
            )
