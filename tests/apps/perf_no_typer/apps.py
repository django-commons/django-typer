from django.apps import AppConfig


class PerfNoTyperConfig(AppConfig):
    name = "tests.apps.perf_no_typer"
    label = name.replace(".", "_")
