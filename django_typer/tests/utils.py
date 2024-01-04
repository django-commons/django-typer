import json
import sys
from pathlib import Path

from django.core.management.color import no_style

DJANGO_PARAMETER_LOG_FILE = Path(__file__).parent / "dj_params.json"


def log_django_parameters(django_command, **extra):
    if DJANGO_PARAMETER_LOG_FILE.exists():
        DJANGO_PARAMETER_LOG_FILE.unlink()

    from django.conf import settings

    with open(DJANGO_PARAMETER_LOG_FILE, "w") as f:
        json.dump(
            {
                "settings": settings.SETTINGS_FILE,
                "python_path": sys.path,
                "no_color": django_command.style == no_style(),
                **extra,
            },
            f,
            indent=4,
        )


def read_django_parameters():
    try:
        with open(DJANGO_PARAMETER_LOG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    finally:
        if DJANGO_PARAMETER_LOG_FILE.exists():
            DJANGO_PARAMETER_LOG_FILE.unlink()
