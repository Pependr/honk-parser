import click

import pathlib
import functools

from typing import Any
from collections.abc import Mapping, Callable

from mdparser import parselib


@click.group("root")
def root() -> None: ...


@root.group("parse", invoke_without_command=True)
@click.pass_context
@click.argument("path", type=click.Path(dir_okay=False, path_type=pathlib.Path))
@click.option("-t", "--target", default=".")
@click.option("-d", "--delim", default="/")
def parse_group(
	ctx: click.Context, path: pathlib.Path, target: str, delim: str
) -> None:
	target_path = parselib.split_obj_path(target, delim)

	data = parselib.resolve_path(parselib.parse_file(path), target_path)

	if target_path[-1] != "*":
		for k, v in data.items():
			if isinstance(v, Mapping):
				continue
			data[k] = {target_path[-1]: v}

	if ctx.invoked_subcommand is None:
		click.echo(data)
	else:
		ctx.ensure_object(dict)
		ctx.obj["DATA"] = data


def template[T](tmp_comm: Callable[..., T]) -> click.Command:
	@parse_group.command
	@click.pass_context
	@functools.wraps(tmp_comm)
	def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> T:
		return ctx.invoke(tmp_comm, ctx.obj["DATA"], *args, **kwargs)

	return wrapper


@template
def table(data: Mapping[str, Mapping[str, Any]]) -> None:
	result: list[str] = []

	header = tuple(data.values())[0].keys()

	result.append(f"||{"|".join(header)}|")

	result.append(f"|{"|".join("-" * (len(header) + 1))}|")

	for k, v in data.items():
		result.append(f"|{k}|{"|".join(str(i) for i in v.values())}|")

	click.echo("\n".join(result))
