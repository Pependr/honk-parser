import pytest
import click.testing

import pathlib
import contextlib

from typing import Generator

from honk import main


type Runner = click.testing.CliRunner


@pytest.fixture
def runner() -> Runner:
    return click.testing.CliRunner()


def invoke_root(runner: Runner, *args: str) -> click.testing.Result:
    return runner.invoke(main.root, args=args, catch_exceptions=False)


@contextlib.contextmanager
def isolated_path(
    runner: Runner,
) -> Generator[pathlib.Path, None, None]:
    with runner.isolated_filesystem() as iso:
        yield pathlib.Path(iso)
