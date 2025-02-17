import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$druy$m$nio-bkagw_%=@(1w)q0=k^mk_5sfk3zi9#4v!%mh*u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = ["tests.apps.util", "autotranslate", "django_typer"]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"
# LANGUAGE_CODE = 'de'

AUTOTRANSLATE_TRANSLATOR_SERVICE = "autotranslate.services.GoogleAPITranslatorService"
GOOGLE_TRANSLATE_KEY = (
    (Path(__file__).parent.parent / "apps/util/google_translate.key")
    .read_text()
    .strip()
)
LOCALE_PATHS = [Path(__file__).parent.parent.parent / "django_typer" / "locale"]
