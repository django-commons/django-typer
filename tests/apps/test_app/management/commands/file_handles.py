import typing as t
from django_typer.management import TyperCommand
from django_typer.completers.path import paths
import typer
from pathlib import Path


class Command(TyperCommand):
    help = "Test command for file handles"

    def handle(
        self,
        file_text: t.Annotated[typer.FileText, typer.Argument(shell_complete=paths)],
        file_text_write: typer.FileTextWrite,
        file_binary: typer.FileBinaryRead,
        file_binary_write: typer.FileBinaryWrite,
    ):
        # workaround
        # if file_text.closed:
        #     file_text = open(file_text.name, "rt", encoding="utf-8")
        # if file_binary.closed:
        #     file_binary = open(file_binary.name, "rb")
        assert file_text.read().strip() == "FileText"
        assert file_binary.read().strip() == b"FileBinary"

        file_text_write.write("FileTextWrite")
        file_binary_write.write(b"FileBinaryWrite")

        file_text_write.close()
        file_binary_write.close()

        assert Path(file_text_write.name).read_text() == "FileTextWrite"
        assert Path(file_binary_write.name).read_bytes() == b"FileBinaryWrite"
