import click

import honk


@honk.parser("mock")
def parse_mock(data: str) -> str:
    return f"Parsed data: {data}"


@honk.parser("txt")
def txt(data: str) -> str:
    return f"Read text: {data}"


type NestedList[T] = list[NestedList[T] | T]


def parse(data: str) -> NestedList[str] | str:
    if "," not in data:
        return data
    return [parse(block) for block in data.split(",")]


@honk.parser("nested")
def nested(data: str) -> NestedList[str] | str:
    truncated = data.replace(" ", "").replace("\n", "")
    return parse(truncated)


@honk.template()
def mock(data: str) -> None:
    click.echo(f"Processed data: {data}")
