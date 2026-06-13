"""A honk plugin which helps you putting number sequences in order"""

import click

import json
import functools
import itertools

from typing import Any, Mapping, Callable, Sequence

import honk


def group(nums: Sequence[int]) -> list[list[int]]:
    if len(nums) == 0:
        return []

    inter: list[list[int]] = [[nums[0]]]

    for a, b in itertools.pairwise(nums):
        if b - a == 1:
            inter[-1].append(b)
        else:
            inter.append([b])

    return inter


def compress(sub: Sequence[int]) -> str:
    if len(sub) == 1:
        return str(sub[0])
    return f"{sub[0]}-{sub[-1]}"


def compress_many(nested: Sequence[Sequence[int]]) -> list[str]:
    return list(map(compress, nested))


def concat(seq: Sequence[str]) -> str:
    if len(seq) == 0:
        return "none"
    return ", ".join(seq)


type NestedMapping[T] = Mapping[str, Mapping[str, T]]


def map_nested[I, O](
    fn: Callable[[I], O], mapping: NestedMapping[I]
) -> NestedMapping[O]:
    return {k: {x: fn(y) for x, y in v.items()} for k, v in mapping.items()}


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def pipe(value: Any) -> Any:
        return functools.reduce(lambda x, f: f(x), funcs, value)

    return pipe


PIPELINE = compose(sorted, group, compress_many, concat)


@honk.template("group", help="Sort and group number sequences")
def _(data: NestedMapping[Sequence[int]]) -> None:
    click.echo(json.dumps(map_nested(PIPELINE, data)))
