import click

import json
import tomllib
import itertools

from typing import Any, Mapping, Sequence

import honk
import honk.parselib


def to_exclude(i: str, exclude: tuple[str, ...]) -> bool:
    return any(honk.parselib.match_wildcard(e, i) for e in exclude)


honk.parser("json")(json.loads)
honk.parser("toml")(tomllib.loads)


@honk.template(help="Print the parsed data as is")
def echo(data: Any) -> None:
    click.echo(data)


@honk.template("json", help="Print the parsed data in json format")
def to_json(data: Any) -> None:
    click.echo(json.dumps(data))


@honk.template(help="Parses nested mappings")
@click.option("--header", default="")
@click.option("--excluded-col", multiple=True)
@click.option("--excluded-row", multiple=True)
@click.option("-s", "--swap", help="Swaps columns and rows", is_flag=True)
def map_map(
    data: Mapping[str, Mapping[str, Any]],
    header: str,
    excluded_col: tuple[str, ...],
    excluded_row: tuple[str, ...],
    swap: bool,
) -> None:
    raw_rows: list[str] = list(data.keys())
    raw_columns: list[str] = []

    for inner in data.values():
        for key in inner.keys():
            if key not in raw_columns:
                raw_columns.append(key)

    if swap:
        raw_rows, raw_columns = raw_columns, raw_rows

    rows: list[str] = [k for k in raw_rows if not to_exclude(k, excluded_row)]
    columns: list[str] = [
        k for k in raw_columns if not to_exclude(k, excluded_col)
    ]

    cols: str = f"|{header}|{"|".join(columns)}|"
    line: str = f"|{"|".join("-" * (len(columns) + 1))}|"

    head: str = f"{cols}\n{line}\n"

    def get(k1: str, k2: str) -> Any:
        if k1 in data.keys():
            return data[k1].get(k2)
        return data[k2].get(k1)

    body: list[str] = [
        f"|{row}|{"|".join(str(get(row, col)) for col in columns)}|"
        for row in rows
    ]

    click.echo(head + "\n".join(body) + "\n")


@honk.template(help="Parses a mapping of arrays")
@click.option("-e", "--excluded", multiple=True)
def map_arr(
    data: Mapping[str, Sequence[Any]], excluded: tuple[str, ...]
) -> None:
    result: list[str] = []

    keys = list(filter(lambda i: not to_exclude(i, excluded), data.keys()))

    result.append(f"|{"|".join(keys)}|")

    result.append(f"|{"|".join("-" * len(keys))}|")

    for row in itertools.zip_longest(*map(lambda k: data[k], keys)):
        result.append(f"|{"|".join(map(str, row))}|")

    click.echo("\n".join(result) + "\n")


@honk.template(help="Parses arrays of mappings")
@click.option("-e", "--excluded", multiple=True)
def arr_map(
    data: Sequence[Mapping[str, Any]], excluded: tuple[str, ...]
) -> None:
    columns: list[str] = []

    for mapping in data:
        for key in mapping.keys():
            if key not in columns and not to_exclude(key, excluded):
                columns.append(key)

    cols: str = f"|{"|".join(columns)}|"
    line: str = f"|{"|".join("-" * len(columns))}|"

    head: str = f"{cols}\n{line}\n"

    body: list[str] = [
        f"|{"|".join(map(str, map(row.get, columns)))}|" for row in data
    ]

    click.echo(head + "\n".join(body) + "\n")
