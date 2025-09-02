from django.apps import AppConfig


class NoTyperConfig(AppConfig):
    name = "profiling.no_typer"
    label = name.replace(".", "_")
