from enum import Enum
from click.shell_completion import add_completion_class


class Shells(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"
    powershell = "powershell"
    pwsh = "pwsh"


def completion_init():
    from .bash import BashComplete
    from .fish import FishComplete
    from .powershell import PowerShellComplete
    from .zsh import ZshComplete

    add_completion_class(BashComplete, Shells.bash)
    add_completion_class(ZshComplete, Shells.zsh)
    add_completion_class(FishComplete, Shells.fish)
    add_completion_class(PowerShellComplete, Shells.powershell)
    add_completion_class(PowerShellComplete, Shells.pwsh)
