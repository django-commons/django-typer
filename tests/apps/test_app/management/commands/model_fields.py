import json
import sys
import typing as t
from typing import Annotated


import typer
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from django_typer.management import (
    TyperCommand,
    command,
    initialize,
    model_parser_completer,
)
from django_typer import types
from django_typer.completers import ModelObjectCompleter
from tests.apps.test_app.models import ShellCompleteTester


def obj_not_found(model_cls, value, exc):
    raise RuntimeError(f"Object {model_cls.__name__} with {value} not found.")


class Command(TyperCommand):
    @initialize()
    def init(self, verbosity: types.Verbosity = 1):
        assert self.__class__ is Command
        self.verbosity = verbosity

    @command()
    def test(
        self,
        char: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "char_field"),
                help=_("Fetch objects by their char fields."),
            ),
        ] = None,
        ichar: Annotated[
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
        text: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
            typer.Option(
                **model_parser_completer(
                    ShellCompleteTester,
                    "text_field",
                    query=ModelObjectCompleter.text_query,
                ),
                help=_("Fetch objects by their text fields."),
            ),
        ] = None,
        itext: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
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
        uuid: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "uuid_field"),
                help=_("Fetch objects by their UUID fields."),
            ),
        ] = None,
        id: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester),
                help=_("Fetch objects by their int (pk) fields."),
            ),
        ] = None,
        id_limit: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, limit=5),
                help=_("Fetch objects by their int (pk) fields."),
            ),
        ] = None,
        float: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "float_field"),
                help=_("Fetch objects by their float fields."),
            ),
        ] = None,
        decimal: Annotated[
            t.Optional[ShellCompleteTester],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "decimal_field"),
                help=_("Fetch objects by their decimal fields."),
            ),
        ] = None,
        ip: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "ip_field"),
                help=_("Fetch objects by their IP address fields."),
            ),
        ] = None,
        email: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "email_field"),
                help=_("Fetch objects by their email fields."),
            ),
        ] = None,
        url: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
            typer.Option(
                **model_parser_completer(ShellCompleteTester, "url_field"),
                help=_("Fetch objects by their url fields."),
            ),
        ] = None,
        filtered: Annotated[
            t.Optional[t.List[ShellCompleteTester]],
            typer.Option(
                **model_parser_completer(
                    ShellCompleteTester.objects.filter(
                        ~(
                            Q(text_field__istartswith="a")
                            | Q(text_field__istartswith="s")
                        )
                    ),
                    "text_field",
                ),
                help=_("Fetch objects by their text fields."),
            ),
        ] = None,
    ):
        assert self.__class__ is Command
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
        if uuid is not None:
            assert isinstance(uuid, ShellCompleteTester)
            objects["uuid"] = {uuid.id: str(uuid.uuid_field)}
        if id is not None:
            assert isinstance(id, ShellCompleteTester)
            objects["id"] = id.pk
        if float is not None:
            assert isinstance(float, ShellCompleteTester)
            objects["float"] = {float.id: str(float.float_field)}
        if decimal is not None:
            assert isinstance(decimal, ShellCompleteTester)
            objects["decimal"] = {decimal.id: str(decimal.decimal_field)}
        if ip is not None:
            for addr in ip:
                assert isinstance(addr, ShellCompleteTester)
            objects["ip"] = [{addr.id: addr.ip_field} for addr in ip]
        if filtered is not None:
            for txt in filtered:
                assert isinstance(txt, ShellCompleteTester)
            objects["filtered"] = [{txt.id: txt.text_field} for txt in filtered]
        return json.dumps(objects)
