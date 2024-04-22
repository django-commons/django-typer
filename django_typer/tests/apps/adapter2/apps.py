from django.apps import AppConfig


class Adapter2Config(AppConfig):
    name = "django_typer.tests.apps.adapter2"
    label = name.replace(".", "_")
    verbose_name = "Adapter 2"

    def ready(self):
        print(self.label)
