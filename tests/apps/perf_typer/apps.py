from django.apps import AppConfig


class PerfTyperConfig(AppConfig):
    name = "tests.apps.perf_typer"
    label = name.replace(".", "_")
