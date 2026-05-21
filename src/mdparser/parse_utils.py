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


# class RegistryError(KeyError): ...


# def parser(ext: str) -> Callable[[ParseStrat], ParseStrat]:
# 	def decorator(fn: ParseStrat) -> ParseStrat:
# 		if ext in PARSE_STRATS:
# 			raise RegistryError(
# 				f"Parser for extension .{ext} is already registered."
# 			)

# 		PARSE_STRATS[ext] = fn

# 		return fn

# 	return decorator


class UnsupportedExtension(ValueError): ...


def parse_file(path: pathlib.Path) -> dict[str, Any]:
	_, ext = path.as_posix().split(".")

	parser = PARSE_STRATS.get(ext)

	if parser is None:
		raise UnsupportedExtension(f"Extension .{ext} is unsupported.")

	return parser(path.read_text())


def split_obj_path(path: str, delim: str = "/") -> list[str]:
	if path == ".":
		return []
	return path.split(delim)


def deep_get(target: Mapping[str, Any], path: Sequence[str]) -> Any:
	return functools.reduce(lambda d, k: d[k], path, target)
