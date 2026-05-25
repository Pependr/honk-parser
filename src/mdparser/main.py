import click

import enum
import functools

from pathlib import Path

from typing import Any, Callable

from mdparser import parselib


@click.group("root")
def root() -> None: ...


@root.group("parse", invoke_without_command=True)
@click.pass_context
@click.argument("path", type=Path)
@click.option("-t", "--target", type=str, default=".")
@click.option("-d", "--delim", type=str, default="/")
def parse_group(
	ctx: click.Context, path: Path, target: str, delim: str
) -> None:
	data = parselib.resolve_wildcard(
		parselib.parse_file(path), parselib.split_obj_path(target, delim)
	)

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


class Align(enum.StrEnum):
	RIGHT = "-:"
	CENTER = ":-:"
	LEFT = ":-"
	NONE = "-"


@template
@click.argument("header", nargs=-1)
@click.option(
	"-a",
	"--align",
	default=Align.NONE,
	type=click.Choice(Align, case_sensitive=False),
)
def table(data: dict[str, Any], header: tuple[str, ...], align: Align) -> None:
	result: list[str] = []

	result.append(f"|{"|".join(header)}|")

	result.append(f"|{"|".join([align.value] * len(header))}|")

	for k, v in data.items():
		result.append(f"|{k}|{v}|")

	click.echo("\n".join(result))
