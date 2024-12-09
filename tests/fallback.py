import typing as t
from click.shell_completion import CompletionItem


def custom_fallback(args: t.List[str], incomplete: str) -> t.List[CompletionItem]:
    return [CompletionItem("custom_fallback")]


def custom_fallback_cmd_str(
    args: t.List[str], incomplete: str
) -> t.List[CompletionItem]:
    return [CompletionItem(" ".join(args) + incomplete)]
