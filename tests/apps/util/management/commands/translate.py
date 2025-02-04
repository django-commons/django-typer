import os
from django.conf import settings
from typer import Argument, Option
import json
import typing as t
import shutil

from django_typer.management import TyperCommand
from pathlib import Path
from django.core.management import call_command
from django.contrib import admindocs

django_typer = Path(__file__).parent.parent.parent.parent.parent.parent / "django_typer"


class Command(TyperCommand):
    help = "(Re)Generate the translations for django-typer help strings."

    def handle(self):
        cwd = os.getcwd()
        # use the languages that django has admin documentation in
        languages = sorted(os.listdir(Path(admindocs.__file__).parent / "locale"))
        # lang_args = (list(itertools.chain.from_iterable(("-l", lang) for lang in languages)))
        try:
            os.chdir(django_typer)

            for lang in languages:
                call_command("makemessages", "-l", lang)
                try:
                    call_command("translate_messages", "-l", lang)
                except Exception as e:
                    self.secho(
                        f"Failed to translate messages for {lang}: {e}", fg="red"
                    )
                    locale_dir = Path(django_typer) / f"locale/{lang}"
                    if locale_dir.is_dir():
                        shutil.rmtree(Path(django_typer) / f"locale/{lang}")
            call_command("compilemessages")
        finally:
            os.chdir(cwd)
