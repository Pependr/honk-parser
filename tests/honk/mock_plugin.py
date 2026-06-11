import click

import honk


@honk.parser("mock")
def parse_mock(data: str) -> str:
    return f"Mock data: {data}"


@honk.template("mock")
def mock(data: str) -> None:
    click.echo(f"Mock data: {data}")
