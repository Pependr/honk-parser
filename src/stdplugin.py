import click

import json
import tomllib

from typing import Any, Mapping, KeysView

from mdparser import parselib, templates


parselib.parser("json")(json.loads)
parselib.parser("toml")(tomllib.loads)


@templates.template
@click.option("--header", default="")
@click.option("-e", "--exclude", multiple=True)
def table(
	data: Mapping[str, Mapping[str, Any]], header: str, exclude: tuple[str, ...]
) -> None:
	result: list[str] = []

	def to_exclude(i: str) -> bool:
		return any(parselib.match_wildcard(e, i) for e in exclude)

	def inner_keys[T](mp: Mapping[Any, Mapping[T, Any]]) -> KeysView[T]:
		return next(iter(mp.values())).keys()

	cols = [i for i in inner_keys(data) if not to_exclude(i)]

	result.append(f"|{header}|{"|".join(cols)}|")

	result.append(f"|{"|".join("-" * (len(cols) + 1))}|")

	for k, v in data.items():
		result.append(
			f"|{k}|{"|".join(str(v[r]) for r in v.keys() if not to_exclude(r))}|"
		)

	click.echo("\n".join(result) + "\n")
