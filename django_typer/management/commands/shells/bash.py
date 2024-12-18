from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from ..shellcompletion import DjangoTyperShellCompleter


class BashComplete(DjangoTyperShellCompleter):
    """
    https://github.com/scop/bash-completion#faq
    """

    name = "bash"
    template = "shell_complete/bash.sh"

    @cached_property
    def install_dir(self) -> Path:
        install_dir = Path.home() / ".bash_completions"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def format_completion(self, item: CompletionItem) -> str:
        return f"{item.type},{item.value}"

    def install_bash(self) -> Path:
        assert self.prog_name
        Path.home().mkdir(parents=True, exist_ok=True)
        script = self.install_dir / f"{self.prog_name}.sh"
        bashrc = Path.home() / ".bashrc"
        bashrc_source = bashrc.read_text() if bashrc.is_file() else ""
        source_line = f"source {script}"
        if source_line not in bashrc_source:
            bashrc_source += f"\n{source_line}\n"
        bashrc.write_text(bashrc_source)
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(self.source())
        return script

    def uninstall(self):
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.sh"
        if script.is_file():
            script.unlink()

        bashrc = Path.home() / ".bashrc"
        if bashrc.is_file():
            bashrc_source = bashrc.read_text()
            bashrc.write_text(bashrc_source.replace(f"source {script}\n", ""))
