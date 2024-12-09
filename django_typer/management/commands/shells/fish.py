from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from ..shellcompletion import DjangoTyperShellCompleter


class FishComplete(DjangoTyperShellCompleter):
    name = "fish"
    SCRIPT = Path(__file__).parent / "fish.fish"

    @cached_property
    def install_dir(self) -> Path:
        """
        The directory where completer scripts will be installed.
        """
        install_dir = Path.home() / ".config/fish/completions"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def format_completion(self, item: CompletionItem) -> str:
        if item.help:
            return f"{item.type},{item.value}\t{item.help}"
        return f"{item.type},{item.value}"

    def install(self) -> Path:
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.fish"
        script.write_text(self.source())
        return script

    def uninstall(self):
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.fish"
        if script.is_file():
            script.unlink()
