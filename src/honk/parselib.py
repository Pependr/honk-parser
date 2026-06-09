import functools

from typing import Any, Callable, Protocol, Sequence, SupportsIndex, cast
from collections.abc import Mapping


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


type NestedData = Mapping[str, Any] | Sequence[Any]
type NestedPath = Sequence[str | SupportsIndex]
type ParseStrat = Callable[[str], NestedData]


PARSE_STRATS: dict[str, ParseStrat] = {}


def parser(ext: str) -> Callable[[ParseStrat], ParseStrat]:
    def decorator(fn: ParseStrat) -> ParseStrat:
        PARSE_STRATS[ext] = fn
        return fn

    return decorator


def get_extension(path: SupportsStr) -> str:
    return str(path).split(".")[-1]


def parse(text: str, method: str) -> NestedData:
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


def deep_get(target: NestedData, path: NestedPath) -> Any:
    return functools.reduce(lambda d, k: d[k], path, target)  # type: ignore


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


def resolve_path(target: NestedData, path: NestedPath, delim: str = "*") -> Any:
    if delim not in path:
        return deep_get(target, path)

    pre, post = split_sequence(path, delim, maxsplit=1)

    def wrap(x: Any) -> Any:
        if path[-1] == delim:
            return x

        resolved = resolve_path(x, post)

        if isinstance(resolved, Mapping):
            return cast(Mapping[str, Any], resolved)

        return {path[-1]: resolved}

    space: Mapping[str, Any] = deep_get(target, pre)

    return {k: wrap(v) for k, v in space.items()}


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
