import click

import honk


@honk.parser("mock")
def parse_mock(data: str) -> str:
    return f"Parsed data: {data}"


@honk.parser("txt")
def txt(data: str) -> str:
    return f"Read text: {data}"


@honk.template("mock")
def mock(data: str) -> None:
    click.echo(f"Processed data: {data}")
