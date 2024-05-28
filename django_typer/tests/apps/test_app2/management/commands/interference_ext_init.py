from django_typer import initialize, command, group
from .interference_ext import Command as InterferenceExt


class Command(InterferenceExt):
    help = "Inherited and extend interference - test classmethod initialize()"

    @InterferenceExt.initialize(invoke_without_command=True)
    def init(self, arg: int = 5):
        return f"test_app2::interference_ext_init::init({arg})"
