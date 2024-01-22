from django.apps import AppConfig


class Adapter1Config(AppConfig):
    name = "django_typer.tests.adapter1"
    label = name.replace(".", "_")
    verbose_name = "Adapter 1"
    
    def ready(self):
        print(self.label)
