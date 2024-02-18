import json
import typing as t

import typer
from django.utils.translation import gettext_lazy as _

from django_typer import (
    TyperCommand,
    command,
    initialize,
    model_parser_completer,
    types,
)
from django_typer.tests.test_app.models import ShellCompleteTester


def obj_not_found(model_cls, value, exc):
    raise RuntimeError(f"Object {model_cls.__name__} with {value} not found.")


class Command(TyperCommand):

    @initialize()
    def init(self, verbosity: types.Verbosity = 1):
        self.verbosity = verbosity

    @command()
    def test(
        self,
        char: t.Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "char_field"),
                help=_("Fetch objects by their char fields."),
            ),
        ] = None,
        ichar: t.Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(
                    ShellCompleteTester,
                    "char_field",
                    case_insensitive=True,
                    on_error=obj_not_found,
                ),
                help=_("Fetch objects by their char fields, case insensitive."),
            ),
        ] = None,
        text: t.Annotated[
            t.List[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "text_field"),
                help=_("Fetch objects by their text fields."),
            ),
        ] = None,
        itext: t.Annotated[
            t.List[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(
                    ShellCompleteTester,
                    "text_field",
                    case_insensitive=True,
                    distinct=False,
                ),
                help=_("Fetch objects by their text fields, case insensitive."),
            ),
        ] = None,
    ):
        assert self.__class__ == Command
        objects = {}
        if char is not None:
            assert isinstance(char, ShellCompleteTester)
            objects["char"] = {char.id: char.char_field}
        if ichar is not None:
            assert isinstance(ichar, ShellCompleteTester)
            objects["ichar"] = {ichar.id: ichar.char_field}
        if text:
            for txt in text:
                assert isinstance(txt, ShellCompleteTester)
            objects["text"] = [{txt.id: txt.text_field} for txt in text]
        if itext:
            for itxt in itext:
                assert isinstance(itxt, ShellCompleteTester)
            objects["itext"] = [{itxt.id: itxt.text_field} for itxt in itext]
        return json.dumps(objects)
