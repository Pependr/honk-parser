import pathlib
import functools

from typing import Any, Callable, Sequence
from collections.abc import Mapping


type ParseStrat = Callable[[str], dict[str, Any]]


PARSE_STRATS: dict[str, ParseStrat] = {}


def parser(ext: str) -> Callable[[ParseStrat], ParseStrat]:
	def decorator(fn: ParseStrat) -> ParseStrat:
		PARSE_STRATS[ext] = fn
		return fn

	return decorator


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
) -> dict[str, Any] | Any:
	if "*" not in path:
		return deep_get(target, path)

	i = path.index("*")
	pre_ast, post_ast = path[:i], path[i + 1 :]

	space: Mapping[str, Any] = deep_get(target, pre_ast)

	data = {k: resolve_path(v, post_ast) for k, v in space.items()}

	if path[-1] != "*":
		for k, v in data.items():
			if isinstance(v, Mapping):
				continue
			data[k] = {path[-1]: v}

	return data


def match_wildcard(pattern: str, string: str) -> bool:
	if "*" not in pattern:
		return string.endswith(pattern)

	i = pattern.find("*")
	pre_ast, post_ast = pattern[:i], pattern[i + 1 :]

	if "*" not in post_ast:
		return string.startswith(pre_ast) and string.endswith(post_ast)

	s = string.removeprefix(pre_ast)

	nxt, *_ = post_ast.split("*")

	while not s.startswith(nxt):
		s = s[1:]

		if s == "":
			break
	else:
		return string.startswith(pre_ast) and match_wildcard(post_ast, s)

	return False
