import pytest
import click.testing

from honk import main


type Runner = click.testing.CliRunner


@pytest.fixture
def runner() -> Runner:
    return click.testing.CliRunner()


def test_help(runner: Runner) -> None:
    result = runner.invoke(main.root, ["--help"])

    assert result.exit_code == 0
    assert "Usage" in result.stdout
