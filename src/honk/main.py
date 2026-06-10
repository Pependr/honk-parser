import click

import sys
import json
import pathlib
import importlib
import contextlib

from typing import Generator

from honk import parselib


@click.group("root", help="A tool for parsing and filtering data")
@click.pass_context
def root(ctx: click.Context) -> None:
    sys.path.append(str(pathlib.Path.cwd().resolve()))

    plugins = pathlib.Path("plugins.json")

    ctx.ensure_object(dict)
    ctx.obj["PLUGINS"] = plugins

    if not plugins.exists():
        importlib.import_module("stdplugin")
        return

    loaded: list[str] = json.loads(plugins.read_text())

    for plugin in loaded:
        importlib.import_module(plugin)


@root.group("parse", help="Parse data from a file or stdin")
@click.pass_context
@click.option(
    "-p",
    "--path",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    default=None,
    help="Path to the file to read from, read from stdin if omitted",
)
@click.option(
    "-m",
    "--method",
    default=None,
    help="Parsing method. Can be omitted when reading from a file, then the file extension is used",
)
@click.option(
    "-t", "--target", default=".", help="The target object in the file"
)
@click.option(
    "-d", "--delim", default="/", help="The delimeter symbol in the target path"
)
def parse_group(
    ctx: click.Context,
    path: pathlib.Path | None,
    method: str | None,
    target: str,
    delim: str,
) -> None:
    if method is None:
        if path is None:
            ctx.fail("Parsing method is required when reading from stdin")
        *_, method = str(path).split(".")

    text: str
    if path is None:
        text = sys.stdin.read()
    else:
        text = path.read_text()

    ctx.obj["DATA"] = parselib.resolve_path(
        parselib.parse(text, method), parselib.split_obj_path(target, delim)
    )


@root.group("plugin", help="Manage your plugins")
@click.pass_context
def plugin_group(ctx: click.Context) -> None:
    path: pathlib.Path = ctx.obj["PLUGINS"]

    if not path.exists():
        path.touch()
        path.write_text(json.dumps(["stdplugin"], indent=4))


@contextlib.contextmanager
def get_loaded(ctx: click.Context) -> Generator[list[str], None, None]:
    path: pathlib.Path = ctx.obj["PLUGINS"]

    loaded: list[str] = json.loads(path.read_text())

    yield loaded

    path.write_text(json.dumps(loaded, indent=4))


@plugin_group.command
@click.pass_context
@click.argument("module")
def load(ctx: click.Context, module: str) -> None:
    with get_loaded(ctx) as loaded:
        if module in loaded:
            ctx.fail(f"Plugin {module} is already loaded")

        loaded.append(module)


@plugin_group.command
@click.pass_context
@click.argument("module")
def unload(ctx: click.Context, module: str) -> None:
    with get_loaded(ctx) as loaded:
        if module not in loaded:
            ctx.fail(f"Plugin {module} is not loaded")

        loaded.remove(module)


@plugin_group.command("list")
@click.pass_context
def list_loaded(ctx: click.Context) -> None:
    with get_loaded(ctx) as loaded:
        click.echo("Loaded plugins:")
        for plugin in loaded:
            click.echo(f"- {plugin}")
