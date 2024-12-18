from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from ..shellcompletion import DjangoTyperShellCompleter


class ZshComplete(DjangoTyperShellCompleter):
    name = "zsh"
    template = "shell_complete/zsh.sh"
    supports_scripts = True

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
        if "fpath+=~/.zfunc" not in zshrc_source:
            zshrc_source += "fpath+=~/.zfunc\n"
        if "autoload -Uz compinit" not in zshrc_source:
            zshrc_source += "autoload -Uz compinit\n"
        if "compinit" not in zshrc_source:
            zshrc_source += "compinit\n"
        style = f"zstyle ':completion:*:*:{self.prog_name}:*' menu select"
        if style not in zshrc_source:
            zshrc_source += f"{style}\n"
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
