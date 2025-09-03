import inspect
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Union
import re
import math
import time
from collections import Counter
import pexpect
from django.core.management.color import no_style
from django_typer import utils

# from charset_normalizer import from_bytes
import platform

rich_installed = utils.rich_installed


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


def strip_control_sequences(text):
    """
    Removes control sequences, such as ANSI escape codes, from the given text.

    Args:
        text (str): The input text containing control sequences.

    Returns:
        str: The cleaned text without control sequences.
    """
    # Regular expression to match ANSI escape codes
    ansi_escape_pattern = re.compile(r"\x1b(?:[@-_][0-?]*[ -/]*[@-~])")
    return ansi_escape_pattern.sub("", text)


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


if platform.system() == "Windows":
    import winpty

    class WinPtyWrapper:
        strip_ansi = True
        buffer = ""

        def __init__(self, command, env=None, cwd=None, strip_ansi=strip_ansi):
            self.strip_ansi = strip_ansi
            self.buffer = ""
            self.process = winpty.PtyProcess.spawn(command, cwd=cwd, env=env)

        def sendline(self, line):
            self.process.write(line + "\r\n")

        def read(self):
            return self.process.read().encode("utf-8")

        def expect(self, pattern, timeout=None):
            if not self.isalive():
                raise EOFError("Process terminated before finding the pattern.")

            start_time = time.time()

            while True:
                if timeout is not None and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Pattern '{pattern}' not found within timeout.")

                chunk = self.read().decode("utf-8")
                if self.strip_ansi:
                    chunk = strip_control_sequences(chunk)
                self.buffer += chunk
                if self.buffer:
                    # Search for the pattern in the buffer
                    match = re.search(pattern, self.buffer)
                    if match:
                        self.buffer = self.buffer[match.end() :]
                        return True

                # Check if the process has ended
                if not self.isalive():
                    raise EOFError("Process terminated before finding the pattern.")

        def isalive(self):
            return self.process.isalive()

        def close(self):
            self.process.close()


def interact(command, *args, **kwargs):
    if platform.system() == "Windows":
        return WinPtyWrapper(
            " ".join([sys.executable, f"./{manage_py.name}", command, *args]),
            env=os.environ,
            cwd=str(manage_py.parent),
        )
    else:
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
    command, *args, parse_json=True, chdir=True, time=False, **kwargs
) -> Union[Tuple[str, str, int], Tuple[str, str, int, float]]:
    # we want to use the same test database that was created for the test suite run
    cwd = os.getcwd()
    try:
        env = kwargs.pop("env") if "env" in kwargs else os.environ.copy()
        if platform.system() == "Windows":
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
        if chdir:
            os.chdir(manage_py.parent)
        cmd = [
            sys.executable,
            f"./{manage_py.name}" if chdir else manage_py,
            command,
            *args,
        ]
        time_seconds = 0.0
        if time:
            cmd.insert(0, "time")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=False,
            env=env,
            **kwargs,
        )
        stdout_encoding = (
            "utf-8"  # getattr(from_bytes(result.stdout).best(), "encoding", "utf-8")
        )
        stdout = result.stdout.decode(stdout_encoding)
        stderr_encoding = (
            "utf-8"  # getattr(from_bytes(result.stderr).best(), "encoding", "utf-8")
        )
        stderr = result.stderr.decode(stderr_encoding)
        if time:
            time_seconds = float(stderr.split("real")[0].strip())

        # Check the return code to ensure the script ran successfully
        if result.returncode != 0:
            return stdout, stderr, result.returncode

        # Parse the output
        if result.stdout:
            if parse_json:
                try:
                    if time:
                        return (
                            json.loads(stdout),
                            stderr,
                            result.returncode,
                            time_seconds,
                        )
                    else:
                        return json.loads(stdout), stderr, result.returncode
                except json.JSONDecodeError:
                    if time:
                        return stdout, stderr, result.returncode, time_seconds
                    return stdout, stderr, result.returncode
            if time:
                return stdout, stderr, result.returncode, time_seconds
            return stdout, stderr, result.returncode
        if time:
            return stdout, stderr, result.returncode, time_seconds
        return stdout, stderr, result.returncode
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


def to_platform_str(path: str) -> str:
    return path.replace("/", os.path.sep)
