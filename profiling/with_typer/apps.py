from django.apps import AppConfig


class WithyperConfig(AppConfig):
    name = "profiling.with_typer"
    label = name.replace(".", "_")
