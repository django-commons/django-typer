from django.apps import AppConfig


class DjangoTyperConfig(AppConfig):
    name = "django_typer"
    label = name.replace(".", "_")
    verbose_name = "Django Typer"
