import json
import pathlib
import tomllib
import functools

from typing import Any, Mapping, Callable, Sequence


type ParseStrat = Callable[[str], dict[str, Any]]


PARSE_STRATS: dict[str, ParseStrat] = {
	"json": json.loads,
	"toml": tomllib.loads,
}


class UnsupportedExtension(ValueError): ...


def parse_file(path: pathlib.Path) -> dict[str, Any]:
	_, ext = path.as_posix().split(".")

	parser = PARSE_STRATS.get(ext)

	if parser is None:
		raise UnsupportedExtension(f"Extension .{ext} is unsupported")

	return parser(path.read_text())


def split_obj_path(path: str, delim: str = "/") -> list[str]:
	if path == ".":
		return []
	return path.strip(delim).split(delim)


def deep_get(target: Mapping[str, Any], path: Sequence[str]) -> Any:
	return functools.reduce(lambda d, k: d[k], path, target)


def resolve_path(
	target: Mapping[str, Any], path: Sequence[str]
) -> dict[str, Any]:
	if "*" not in path:
		return deep_get(target, path)

	i = path.index("*")
	pre_ast, post_ast = path[:i], path[i + 1 :]

	space: Mapping[str, Any] = deep_get(target, pre_ast)

	return {k: resolve_path(v, post_ast) for k, v in space.items()}
