import functools

from typing import Any, Mapping, Callable, Protocol, Sequence, SupportsIndex


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


type ParseStrat = Callable[[str], Any]


PARSE_STRATS: dict[str, ParseStrat] = {}


def parser(ext: str) -> Callable[[ParseStrat], ParseStrat]:
    def decorator(fn: ParseStrat) -> ParseStrat:
        PARSE_STRATS[ext] = fn
        return fn

    return decorator


def get_extension(path: SupportsStr) -> str:
    return str(path).split(".")[-1]


def parse(text: str, method: str) -> Any:
    parser = PARSE_STRATS.get(method)

    if parser is None:
        raise ValueError(f"No such parsing method: {method}")

    return parser(text)


def split_obj_path(path: str, delim: str = "/") -> tuple[str | int, ...]:
    if path == ".":
        return ()

    def transform(x: str) -> str | int:
        if x.isdecimal():
            return int(x)
        return x

    raw = path.strip(delim).split(delim)

    return tuple(map(transform, raw))


def deep_get(target: Any, path: Sequence[str | SupportsIndex]) -> Any:
    return functools.reduce(lambda d, k: d[k], path, target)


def split_sequence[T](
    seq: Sequence[T], delim: T, *, maxsplit: int | None = None
) -> tuple[Sequence[T], ...]:
    if maxsplit is None:
        maxsplit = seq.count(delim)

    if maxsplit == 0:
        return (seq,)

    i = seq.index(delim)

    return (
        seq[:i],
        *split_sequence(seq[i + 1 :], delim, maxsplit=(maxsplit - 1)),
    )


def resolve_path(
    target: Any, path: Sequence[str | SupportsIndex], delim: str = "*"
) -> Any:
    if delim not in path:
        return deep_get(target, path)

    pre, post = split_sequence(path, delim, maxsplit=1)

    space: Mapping[str, Any] = deep_get(target, pre)

    return {k: resolve_path(v, post, delim) for k, v in space.items()}


def match_wildcard(pattern: str, string: str, delim: str = "*") -> bool:
    if delim not in pattern:
        return string == pattern

    pre, post = pattern.split(delim, maxsplit=1)

    if not string.startswith(pre):
        return False

    if delim not in post:
        return string.endswith(post)

    mid, _ = post.split(delim, maxsplit=1)

    while not string.startswith(mid):
        string = string[1:]

    return match_wildcard(post, string, delim)
