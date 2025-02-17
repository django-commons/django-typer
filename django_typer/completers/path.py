import os
import sys
import typing as t
from functools import partial
from pathlib import Path

from click import Context, Parameter
from click.shell_completion import CompletionItem
from django.conf import settings


def _settings_path(name: str) -> t.Optional[Path]:
    s_pth = getattr(settings, name, None)
    if s_pth:
        return Path(s_pth)
    return None


def import_paths(
    ctx: Context,
    param: Parameter,
    incomplete: str,
    root: t.Union[t.Callable[[], t.Optional[Path]], t.Optional[Path]] = None,
) -> t.List[CompletionItem]:
    """
    A completer that completes a python dot import path string based on sys.path.

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :param root: The root path to search for modules.
    :return: A list of available matching import paths
    """
    import pkgutil

    rt = root() if callable(root) else root
    incomplete = incomplete.strip()
    completions = []
    packages = [pkg for pkg in incomplete.split(".") if pkg]
    pkg_complete = not incomplete or incomplete.endswith(".")
    module_import = ".".join(packages) if pkg_complete else ".".join(packages[:-1])
    module_path = Path(module_import.replace(".", "/"))
    search_paths = []

    if rt and (rt / module_path).exists():
        search_paths.append(str(rt / module_path))
    else:
        for pth in sys.path:
            if (Path(pth) / module_path).exists():
                search_paths.append(str(Path(pth) / module_path))

    prefix = "" if pkg_complete else packages[-1]
    for module in pkgutil.iter_modules(path=search_paths):
        if module.name.startswith(prefix):
            completions.append(
                CompletionItem(
                    f"{module_import}{'.' if module_import else ''}{module.name}",
                    type="plain",
                )
            )
    if len(completions) == 1 and not completions[0].value.endswith("."):
        return import_paths(ctx, param, f"{completions[0].value}.") or completions
    return completions


def paths(
    ctx: Context,
    param: Parameter,
    incomplete: str,
    dir_only: t.Optional[bool] = None,
    root: t.Union[t.Callable[[], t.Optional[Path]], t.Optional[Path]] = None,
) -> t.List[CompletionItem]:
    """
    A completer that completes a path. Relative incomplete paths are interpreted
    relative to the current working directory.

    :param ctx: The click context.
    :param param: The click parameter.
    :param incomplete: The incomplete string.
    :param dir_only: Restrict completions to paths to directories only, otherwise
        complete directories or files.
    :param root: Restrict completions to this root path.
    :return: A list of available matching directories
    """
    rt = root() if callable(root) else root

    def exists(pth: Path) -> bool:
        if dir_only:
            return pth.is_dir()
        return pth.exists() or pth.is_symlink()

    separator = os.sep
    if "/" in incomplete:
        if "\\" not in incomplete:
            separator = "/"
    elif "\\" in incomplete:
        separator = "\\"

    completions = []
    if rt:
        incomplete_path = rt / Path(
            incomplete.replace(separator, os.path.sep).lstrip(os.path.sep)
        )
    else:
        incomplete_path = Path(incomplete.replace(separator, os.path.sep))
    partial_dir = ""
    if not exists(incomplete_path) and not incomplete.endswith(separator):
        partial_dir = incomplete_path.name
        incomplete_path = incomplete_path.parent
    elif incomplete_path.is_file() and not dir_only:
        return [CompletionItem(incomplete, type="file")]
    if incomplete_path.is_dir():
        for child in os.listdir(incomplete_path):
            if not exists(incomplete_path / child):
                continue
            if child.startswith(partial_dir):
                to_complete = incomplete[0 : (-len(partial_dir) or None)]
                sep = (
                    ""
                    if not to_complete or to_complete.endswith(separator)
                    else separator
                )
                ctype = (
                    "plain"
                    if rt
                    else "dir"
                    if (incomplete_path / child).is_dir()
                    else "file"
                )
                completions.append(
                    CompletionItem(
                        f"{to_complete}{sep}{child}",
                        type=ctype,
                    )
                )
    if (
        len(completions) == 1
        and Path(completions[0].value).is_dir()
        and [
            child
            for child in os.listdir(completions[0].value)
            if exists(Path(completions[0].value) / child)
        ]
    ):
        # recurse because we can go futher
        return paths(ctx, param, completions[0].value, dir_only=dir_only)
    return completions


directories = partial(paths, dir_only=True)
"""
A completer that completes a directory path (but not files). Relative incomplete paths
are interpreted relative to the current working directory.

:param ctx: The click context.
:param param: The click parameter.
:param incomplete: The incomplete string.
:return: A list of available matching directories
"""


static_paths = partial(paths, root=partial(_settings_path, name="STATIC_ROOT"))
"""
Complete static file paths.

:param ctx: The click context.
:param param: The click parameter.
:param incomplete: The incomplete string.
:param dir_only: Restrict completions to paths to directories only, otherwise
    complete directories or files.
:return: A list of available matching directories
"""

media_paths = partial(paths, root=partial(_settings_path, name="MEDIA_ROOT"))
"""
Complete media file paths.

:param ctx: The click context.
:param param: The click parameter.
:param incomplete: The incomplete string.
:param dir_only: Restrict completions to paths to directories only, otherwise
    complete directories or files.
:return: A list of available matching directories
"""
