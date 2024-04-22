import json
import sys
from pathlib import Path

from django.core.management.color import no_style

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import pexpect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import rich

    rich_installed = True
except ImportError:
    rich_installed = False


DJANGO_PARAMETER_LOG_FILE = Path(__file__).parent / "dj_params.json"
manage_py = Path(__file__).parent.parent.parent / "manage.py"
TESTS_DIR = Path(__file__).parent


def similarity(text1, text2):
    """
    Compute the cosine similarity between two texts.
    https://en.wikipedia.org/wiki/Cosine_similarity

    We use this to lazily evaluate the output of --help to our
    renderings.
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]


def get_named_arguments(function):
    sig = inspect.signature(function)
    return [
        name
        for name, param in sig.parameters.items()
        if param.default != inspect.Parameter.empty
    ]


def interact(command, *args, **kwargs):
    cwd = os.getcwd()
    try:
        os.chdir(manage_py.parent)
        return pexpect.spawn(
            " ".join([sys.executable, f"./{manage_py.name}", command, *args]),
            env=os.environ,
            **kwargs,
        )
    finally:
        os.chdir(cwd)


def run_command(command, *args, parse_json=True, **kwargs) -> Tuple[str, str]:
    # we want to use the same test database that was created for the test suite run
    cwd = os.getcwd()
    try:
        env = os.environ.copy()
        os.chdir(manage_py.parent)
        result = subprocess.run(
            [sys.executable, f"./{manage_py.name}", command, *args],
            capture_output=True,
            text=True,
            env=env,
            **kwargs,
        )

        # Check the return code to ensure the script ran successfully
        if result.returncode != 0:
            return result.stdout, result.stderr, result.returncode

        # Parse the output
        if result.stdout:
            if parse_json:
                try:
                    return json.loads(result.stdout), result.stderr, result.returncode
                except json.JSONDecodeError:
                    return result.stdout, result.stderr, result.returncode
            return result.stdout, result.stderr, result.returncode
        return result.stdout, result.stderr, result.returncode
    finally:
        os.chdir(cwd)


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
                "no_color_attr": django_command.no_color,
                "force_color_attr": django_command.force_color,
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
