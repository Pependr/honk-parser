import argparse
import functools

from typing import Any, Callable, Sequence


type PipePart[T] = Callable[[argparse.Namespace, T], list[str]]


def compose[T](*funcs: PipePart[T]) -> PipePart[T]:
	def pipe(namespace: argparse.Namespace, data: T) -> list[str]:
		def add(lt: list[str], fn: PipePart[T]) -> list[str]:
			return lt + fn(namespace, data)

		return functools.reduce(add, funcs, [])

	return pipe


TEMPLATES: dict[str, PipePart[Any]] = {}


class RegistryError(KeyError): ...


def template[T](name: str) -> Callable[[PipePart[T]], PipePart[T]]:
	def decorator(fn: PipePart[T]) -> PipePart[T]:
		if name in TEMPLATES:
			raise RegistryError(f"Template {name} is already registered")

		TEMPLATES[name] = fn

		return fn

	return decorator


def resolve(template: str) -> PipePart[Any]:
	pipe = TEMPLATES.get(template)

	if pipe is None:
		raise RegistryError(f"No such template: {template}")

	return pipe


def merge(strings: Sequence[str]) -> str:
	return "\n".join(strings)
