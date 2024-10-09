import inspect
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple
import re
import math
import re
from collections import Counter
import pexpect
from django.core.management.color import no_style

try:
    import rich

    rich_installed = True
except ImportError:
    rich_installed = False


TESTS_DIR = Path(__file__).parent
DJANGO_PARAMETER_LOG_FILE = TESTS_DIR / "dj_params.json"
manage_py = TESTS_DIR.parent / "manage.py"
WORD = re.compile(r"\w+")


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)


def similarity(text1, text2):
    """
    Compute the cosine similarity between two texts.
    https://en.wikipedia.org/wiki/Cosine_similarity

    We use this to lazily evaluate the output of --help to our
    renderings.
    #"""
    vector1 = text_to_vector(text1)
    vector2 = text_to_vector(text2)
    return get_cosine(vector1, vector2)


def get_named_arguments(function):
    sig = inspect.signature(function)
    return [
        name
        for name, param in sig.parameters.items()
        if param.default != inspect.Parameter.empty
    ]


def get_named_defaults(function):
    sig = inspect.signature(function)
    return {
        name: param.default
        for name, param in sig.parameters.items()
        if param.default != inspect.Parameter.empty
    }


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


def run_command(
    command, *args, parse_json=True, chdir=True, **kwargs
) -> Tuple[str, str, int]:
    # we want to use the same test database that was created for the test suite run
    cwd = os.getcwd()
    try:
        env = os.environ.copy()
        if chdir:
            os.chdir(manage_py.parent)
        result = subprocess.run(
            [
                sys.executable,
                f"./{manage_py.name}" if chdir else manage_py,
                command,
                *args,
            ],
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
