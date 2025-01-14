import os
from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from . import DjangoTyperShellCompleter


class ZshComplete(DjangoTyperShellCompleter):
    """
    This completer class supports Zsh_. Completion scripts are installed to the ``.zfunc``
    directory in the user's home directory. Style and completion initialization instructions
    are added to the user's ``.zshrc`` file if needed.

    Returned suggestions are delimited by newlines. Each suggestion is on three lines:

    * The first line is the type of the completion.
    * The second line is the value of the completion.
    * The third line is the help text for the completion.

    See also: https://github.com/zsh-users/zsh-completions/blob/master/zsh-completions-howto.org
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
    Zsh_ does support ansi control codes in completion suggestions, but we disable them by
    default.
    """

    @cached_property
    def install_dir(self) -> Path:
        """
        The directory where completer scripts will be installed.
        """
        install_dir = Path.home() / ".zfunc"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def format_completion(self, item: CompletionItem) -> str:
        def escape(s: str) -> str:
            return (
                s.replace('"', '""')
                .replace("'", "''")
                .replace("$", "\\$")
                .replace("`", "\\`")
                .replace(":", r"\\:")
            )

        return f"{item.type}\n{escape(self.process_rich_text(item.value))}\n{escape(self.process_rich_text(item.help)) if item.help else '_'}"

    def install(self) -> Path:
        assert self.prog_name
        Path.home().mkdir(parents=True, exist_ok=True)
        zshrc = Path.home() / ".zshrc"
        zshrc_source = ""
        if zshrc.is_file():
            zshrc_source = zshrc.read_text()
        if "fpath" not in zshrc_source:
            zshrc_source += f"if type brew &>/dev/null; then{os.linesep}"
            zshrc_source += f"\tfpath=(~/.zfunc $(brew --prefix)/share/zsh-completions $fpath){os.linesep}"
            zshrc_source += f"else{os.linesep}"
            zshrc_source += f"\tfpath=(~/.zfunc $fpath){os.linesep}"
            zshrc_source += f"fi{os.linesep}{os.linesep}"
        if "compinit" not in zshrc_source:
            zshrc_source += f"autoload -Uz compinit{os.linesep}"
            zshrc_source += f"compinit{os.linesep}"

        style = f"zstyle ':completion:*:*:{self.prog_name}:*' menu select"
        if style not in zshrc_source:
            zshrc_source += f"{style}{os.linesep}"
        zshrc.write_text(zshrc_source)
        script = self.install_dir / f"_{self.prog_name}"
        script.write_text(self.source())
        return script

    def uninstall(self):
        script = self.install_dir / f"_{self.prog_name}"
        if script.is_file():
            script.unlink()

        zshrc = Path.home() / ".zshrc"
        if zshrc.is_file():
            zshrc_source = zshrc.read_text()
            zshrc.write_text(
                zshrc_source.replace(
                    f"zstyle ':completion:*:*:{self.prog_name}:*' menu select\n", ""
                )
            )
