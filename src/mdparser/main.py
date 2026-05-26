import click

import json
import pathlib
import importlib
import contextlib

from typing import Generator

from mdparser import parselib


@click.group("root", help="A tool for parsing and filtering data")
@click.pass_context
def root(ctx: click.Context) -> None:
	plugins = pathlib.Path("plugins.json")

	ctx.ensure_object(dict)
	ctx.obj["PLUGINS"] = plugins

	if not plugins.exists():
		importlib.import_module("stdplugin")
		return

	to_load: list[str] = json.loads(plugins.read_text())

	for plugin in to_load:
		importlib.import_module(plugin)


@root.group(
	"parse", help="Parse data from a file accordingly to the chosen template"
)
@click.pass_context
@click.argument("path", type=click.Path(dir_okay=False, path_type=pathlib.Path))
@click.option(
	"-t", "--target", default=".", help="The target object in the file"
)
@click.option(
	"-d", "--delim", default="/", help="The delimeter symbol in the target path"
)
def parse_group(
	ctx: click.Context, path: pathlib.Path, target: str, delim: str
) -> None:
	ctx.obj["DATA"] = parselib.resolve_path(
		parselib.parse_file(path), parselib.split_obj_path(target, delim)
	)


@root.group("plugin", help="Manage your plugins")
@click.pass_context
def plugin_group(ctx: click.Context) -> None:
	path: pathlib.Path = ctx.obj["PLUGINS"]

	if not path.exists():
		path.touch()
		path.write_text(json.dumps(["stdplugin"], indent=4))


@contextlib.contextmanager
@click.pass_context
def get_loaded(ctx: click.Context) -> Generator[list[str], None, None]:
	path: pathlib.Path = ctx.obj["PLUGINS"]

	loaded: list[str] = json.loads(path.read_text())

	yield loaded

	path.write_text(json.dumps(loaded, indent=4))


@plugin_group.command
@click.pass_context
@click.argument("module")
def load(ctx: click.Context, module: str) -> None:
	with get_loaded() as loaded:
		if module in loaded:
			ctx.fail(f"Plugin {module} is already loaded")

		loaded.append(module)


@plugin_group.command
@click.pass_context
@click.argument("module")
def unload(ctx: click.Context, module: str) -> None:
	with get_loaded() as loaded:
		if module not in loaded:
			ctx.fail(f"Plugin {module} is not loaded")

		loaded.remove(module)


@plugin_group.command("list")
@click.pass_context
def list_loaded(ctx: click.Context) -> None:
	with get_loaded() as loaded:
		click.echo("Loaded plugins:")
		for plugin in loaded:
			click.echo(f"- {plugin}")
