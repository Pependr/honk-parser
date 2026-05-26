import click

import json
import tomllib
import itertools

from typing import Any, Mapping, KeysView, Sequence

from honk import parselib, templates


def to_exclude(i: str, exclude: tuple[str, ...]) -> bool:
	return any(parselib.match_wildcard(e, i) for e in exclude)


parselib.parser("json")(json.loads)
parselib.parser("toml")(tomllib.loads)


@templates.template(help="Print the parsed data as is")
def debug(data: Any) -> None:
	click.echo(data)


@templates.template(help="Print the parsed data in json format")
def pick(data: Any) -> None:
	click.echo(json.dumps(data))


@templates.template(
	help="Put the nested data in a table, where the keys of the parent object are rows and the keys of the inner objects are the columns"
)
@click.option("--header", default="")
@click.option("-e", "--exclude", multiple=True)
def named_table(
	data: Mapping[str, Mapping[str, Any]], header: str, exclude: tuple[str, ...]
) -> None:
	result: list[str] = []

	def inner_keys[T](mp: Mapping[Any, Mapping[T, Any]]) -> KeysView[T]:
		return next(iter(mp.values())).keys()

	cols = [i for i in inner_keys(data) if not to_exclude(i, exclude)]

	result.append(f"|{header}|{"|".join(cols)}|")

	result.append(f"|{"|".join("-" * (len(cols) + 1))}|")

	for k, v in data.items():
		result.append(
			f"|{k}|{"|".join(str(v[r]) for r in v.keys() if not to_exclude(r, exclude))}|"
		)

	click.echo("\n".join(result) + "\n")


@templates.template(
	help="Put data into a table, where every key of the object is a column"
)
@click.option("-e", "--exclude", multiple=True)
def nameless_table(
	data: Mapping[str, Sequence[Any]], exclude: tuple[str, ...]
) -> None:
	result: list[str] = []

	keys = [k for k in data.keys() if not to_exclude(k, exclude)]

	result.append(f"|{"|".join(keys)}|")

	result.append(f"|{"|".join("-" * len(keys))}|")

	for row in itertools.zip_longest(*[data[k] for k in keys]):
		result.append(f"|{"|".join(map(str, row))}|")

	click.echo("\n".join(result) + "\n")
