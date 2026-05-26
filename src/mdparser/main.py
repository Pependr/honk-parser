import click

import pathlib

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
	if ctx.invoked_subcommand is None:
		ctx.fail("No template provided")

	ctx.ensure_object(dict)

	ctx.obj["DATA"] = parselib.resolve_path(
		parselib.parse_file(path), parselib.split_obj_path(target, delim)
	)
