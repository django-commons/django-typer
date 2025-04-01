import typing as t
from django.db import models
from tests.apps.test_app.models import ChoicesShellCompleteTester


def get_ip_choices() -> t.List[t.Tuple[str, str]]:
    return ChoicesShellCompleteTester.IP_CHOICES


class ChoicesShellCompleteTesterDJ5Plus(models.Model):
    CHAR_CHOICES = ChoicesShellCompleteTester.CHAR_CHOICES

    char_choice = models.CharField(
        max_length=12,
        choices=CHAR_CHOICES,
        db_index=True,
        default=None,
        null=True,
    )

    INT_CHOICES = {k: v for k, v in ChoicesShellCompleteTester.INT_CHOICES}

    int_choice = models.PositiveSmallIntegerField(
        choices=INT_CHOICES,
        db_index=True,
        default=None,
        null=True,
    )

    ip_choice = models.GenericIPAddressField(
        choices=get_ip_choices,
        db_index=True,
        default=None,
        null=True,
    )
