import os
from django.conf import settings
import typer
import json
import typing as t
import shutil

from django_typer.management import TyperCommand
from pathlib import Path
from django.core.management import call_command
from django.contrib import admindocs

django_typer = Path(__file__).parent.parent.parent.parent.parent.parent / "django_typer"
# temp_typer_link = django_typer / "typer"


class Command(TyperCommand):
    help = "(Re)Generate the translations for django-typer help strings."

    def handle(self):
        cwd = os.getcwd()
        # if temp_typer_link.is_symlink():
        #     os.unlink(temp_typer_link)
        # os.symlink(Path(typer.__file__).parent, temp_typer_link)
        # use the languages that django has admin documentation in
        languages = sorted(os.listdir(Path(admindocs.__file__).parent / "locale"))
        # lang_args = (list(itertools.chain.from_iterable(("-l", lang) for lang in languages)))
        try:
            os.chdir(django_typer)

            for lang in languages:
                locale_dir = Path(django_typer) / f"locale/{lang}"
                call_command("makemessages", "-l", lang, symlinks=True)
                try:
                    call_command("translate_messages", "-l", lang)
                    po_file = locale_dir / "LC_MESSAGES" / "django.po"
                    if po_file.is_file():
                        po = po_file.read_text()
                        if "&quot;" in po:
                            po_file.write_text(po.replace("&quot;", '\\"'))
                except Exception as e:
                    self.secho(
                        f"Failed to translate messages for {lang}: {e}", fg="red"
                    )
                    if locale_dir.is_dir():
                        shutil.rmtree(Path(django_typer) / f"locale/{lang}")
            call_command("compilemessages")
        finally:
            os.chdir(cwd)
            # if temp_typer_link.is_symlink():
            #    os.unlink(temp_typer_link)
